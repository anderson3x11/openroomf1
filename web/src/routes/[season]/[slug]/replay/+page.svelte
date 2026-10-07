<script lang="ts">
	import Panel from '#lib/components/Panel.svelte';
	import TeamMark from '#lib/components/TeamMark.svelte';
	import { getRace } from '#lib/race.ts';
	import { tyreColor } from '#lib/tyres.ts';
	import type { Replay } from '#lib/types.ts';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const race = getRace();

	// Fetched on demand: the replay is too big to be part of every page.
	let replay = $state<Replay | null>(null);
	let failed = $state(false);
	$effect(() => {
		const url = `/${data.meta.season}/${data.meta.slug}/replay.json`;
		replay = null;
		fetch(url)
			.then((r) => r.json())
			.then((r: Replay | null) => {
				replay = r;
				failed = r === null;
			})
			.catch(() => (failed = true));
	});

	const SPEEDS = [1, 4, 16, 64];
	let frame = $state(0); // fractional index into the replay frames
	let playing = $state(false);
	let speed = $state(16);
	let names = $state(true);
	// Drivers picked in the running order: they stay bright, everyone else is dimmed.
	let selected = $state(new Set<string>());

	$effect(() => {
		if (!playing || !replay) return;
		const r = replay;
		let last = performance.now();
		let id = requestAnimationFrame(function tick(now) {
			frame = Math.min(r.n - 1, frame + (((now - last) / 1000) * speed) / r.dt);
			last = now;
			if (frame >= r.n - 1) playing = false;
			else id = requestAnimationFrame(tick);
		});
		return () => cancelAnimationFrame(id);
	});

	function seek(seconds: number) {
		if (replay) frame = Math.min(replay.n - 1, Math.max(0, frame + seconds / replay.dt));
	}
	function changeSpeed(step: number) {
		const i = SPEEDS.indexOf(speed) + step;
		speed = SPEEDS[Math.min(SPEEDS.length - 1, Math.max(0, i))];
	}
	/** Click: follow one driver (click again to clear). Shift click: add or remove him. */
	function pick(drv: string, add: boolean) {
		if (add) {
			const next = new Set(selected);
			if (next.has(drv)) next.delete(drv);
			else next.add(drv);
			selected = next;
		} else {
			selected = selected.size === 1 && selected.has(drv) ? new Set() : new Set([drv]);
		}
	}

	function onkey(e: KeyboardEvent) {
		const tag = (e.target as HTMLElement).tagName;
		if (!replay || tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA') return;
		const step = e.shiftKey ? 60 : 10;
		const actions: Record<string, () => void> = {
			' ': () => (playing = !playing),
			ArrowLeft: () => seek(-step),
			ArrowRight: () => seek(step),
			ArrowUp: () => changeSpeed(1),
			ArrowDown: () => changeSpeed(-1),
			r: () => ((frame = 0), (playing = false)),
			l: () => (names = !names),
			Escape: () => (selected = new Set())
		};
		const action = actions[e.key] ?? actions[e.key.toLowerCase()];
		if (action) {
			e.preventDefault();
			action();
		}
	}

	const byDrv = $derived(new Map(data.results.map((r) => [r.drv, r])));
	const t = $derived(replay ? replay.t0 + frame * replay.dt : 0);
	const lapsDone = $derived(replay ? replay.laps.filter((l) => l <= t).length : 0);
	const lap = $derived(Math.min(lapsDone + 1, data.positions.laps));
	const elapsed = $derived(replay ? Math.max(0, t - replay.t0 - 10) : 0); // t0 is 10 s before the start
	const clock = $derived(
		`${Math.floor(elapsed / 3600)}:${String(Math.floor((elapsed % 3600) / 60)).padStart(2, '0')}:${String(Math.floor(elapsed % 60)).padStart(2, '0')}`
	);

	/** Position at the current fractional frame, linearly interpolated. */
	function at(xy: (number | null)[] | undefined, f: number): [number, number] | null {
		if (!xy) return null;
		const i = Math.floor(f);
		const k = f - i;
		const [x0, y0, x1, y1] = [xy[2 * i], xy[2 * i + 1], xy[2 * i + 2], xy[2 * i + 3]];
		if (x0 == null || y0 == null) return null;
		if (x1 == null || y1 == null) return [x0, y0];
		return [x0 + (x1 - x0) * k, y0 + (y1 - y0) * k];
	}

	const shown = (drv: string) => (selected.size ? selected.has(drv) : race.filters.drivers.has(drv));
	const cars = $derived(
		replay
			? Object.entries(replay.cars)
					.map(([drv, xy]) => ({ drv, p: at(xy, frame), r: byDrv.get(drv) }))
					.filter((c): c is typeof c & { p: [number, number] } => c.p !== null)
					// Highlighted cars are drawn last, on top of the others.
					.sort((a, b) => Number(selected.has(a.drv)) - Number(selected.has(b.drv)))
			: []
	);
	const sc = $derived(replay ? at(replay.sc, frame) : null);

	const FINISHED = new Set(['Finished', 'Lapped']);
	/** Running order at the end of the last lap completed by the leader, with tyre and gap.
	 * Finishers keep their last position, retired drivers are listed as OUT. */
	const tower = $derived(
		Object.entries(data.positions.pos)
			.map(([drv, pos]) => {
				const last = pos.findLastIndex((p) => p !== null);
				const done = Math.min(lapsDone, last);
				const out = last < lapsDone && !FINISHED.has(byDrv.get(drv)?.status ?? '');
				const stint = data.strategy.find((s) => s.drv === drv && done + 1 >= s.from && done + 1 <= s.to)
					?? data.strategy.findLast((s) => s.drv === drv && s.from <= done + 1);
				return { drv, pos: pos[done], out, cmp: stint?.cmp, gap: data.gaps.gap[drv]?.[done] ?? null };
			})
			.filter((d) => d.pos != null)
			.sort((a, b) => Number(a.out) - Number(b.out) || (a.pos as number) - (b.pos as number))
	);
	const fmtGap = (g: number | null, pos: number | null) =>
		pos === 1 ? 'LEADER' : g === null ? '' : `+${g < 60 ? g.toFixed(1) : `${Math.floor(g / 60)}:${(g % 60).toFixed(0).padStart(2, '0')}`}`;
	const points = $derived(data.circuit?.path.map(([x, y]) => `${x},${y}`).join(' ') ?? '');
</script>

<svelte:window onkeydown={onkey} />

<div class="panels">
	<Panel
		title="Race replay"
		desc="Every car on track, one position per second, from the official timing data. The safety car is simulated just ahead of the leader: F1 does not publish its position."
		wide
	>
		{#if failed || !data.circuit}
			<p class="label">[ NO REPLAY ] Position data is not available for this Grand Prix.</p>
		{:else if !replay}
			<p class="label">[ LOADING REPLAY ]</p>
		{:else}
			<div class="controls">
				<button class="label primary" onclick={() => (playing = !playing)}>
					{playing ? '[ PAUSE ]' : '[ PLAY ]'}
				</button>
				<button class="label" onclick={() => seek(-10)} title="Back 10 s (left arrow)">-10S</button>
				<button class="label" onclick={() => seek(10)} title="Forward 10 s (right arrow)">+10S</button>
				<span class="label gap">SPEED</span>
				{#each SPEEDS as s (s)}
					<button class="label" aria-pressed={speed === s} onclick={() => (speed = s)}>x{s}</button>
				{/each}
				<button class="label gap" aria-pressed={names} onclick={() => (names = !names)}>NAMES</button>
				{#if selected.size}
					<button class="label" onclick={() => (selected = new Set())}>[ CLEAR SELECTION ]</button>
				{/if}
				<span class="label readout">LAP <b>{lap}/{data.positions.laps}</b> / <b>{clock}</b></span>
			</div>
			<input
				class="scrub"
				type="range"
				min="0"
				max={replay.n - 1}
				step="1"
				aria-label="Replay position"
				value={Math.round(frame)}
				oninput={(e) => (frame = e.currentTarget.valueAsNumber)}
			/>
			<p class="label keys">
				SPACE play / pause, LEFT RIGHT 10 s (SHIFT 1 min), UP DOWN speed, R restart, L names. Click a
				driver to follow him, SHIFT click for several, ESC to clear.
			</p>
			<div class="stage">
				<svg viewBox="-20 -20 {data.circuit.w + 40} {data.circuit.h + 40}" role="img" aria-label="Track map">
					<polygon class="track" {points} />
					{#each cars as c (c.drv)}
						<g
							class="car"
							class:dim={!shown(c.drv)}
							class:picked={selected.has(c.drv)}
							transform="translate({c.p[0]} {c.p[1]})"
						>
							<circle r={selected.has(c.drv) ? 17 : 13} fill={c.r?.color ?? 'var(--ink-muted)'} />
							{#if names || selected.has(c.drv)}<text x="20" y="7">{c.drv}</text>{/if}
						</g>
					{/each}
					{#if sc}
						<g class="sc" transform="translate({sc[0]} {sc[1]})">
							<circle class="halo" r="26" />
							<circle r="15" />
							<text x="22" y="7">SC</text>
						</g>
					{/if}
				</svg>
				<ol class="tower">
					{#each tower as d (d.drv)}
						{@const r = byDrv.get(d.drv)}
						<li>
							<button
								class:dim={!shown(d.drv)}
								aria-pressed={selected.has(d.drv)}
								onclick={(e) => pick(d.drv, e.shiftKey)}
							>
								<span class="pos">{d.out ? 'OUT' : d.pos}</span>
								<TeamMark src={r && race.logos[r.tid]} color={r?.color} team={r?.team ?? ''} />
								<b>{d.drv}</b>
								{#if d.cmp && !d.out}<span
										class="tyre"
										style:background={tyreColor(d.cmp)}
										title={d.cmp}
									></span>{/if}
								<span class="gap-value">{d.out ? '' : fmtGap(d.gap, d.pos)}</span>
							</button>
						</li>
					{/each}
				</ol>
			</div>
		{/if}
	</Panel>
</div>

<style>
	.controls {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 8px;
		margin-bottom: 10px;
	}
	button {
		background: none;
		border: 1px solid var(--rule);
		padding: 6px 10px;
		cursor: pointer;
		color: var(--ink-muted);
		touch-action: manipulation;
	}
	button[aria-pressed='true'],
	.primary {
		color: var(--ink);
		border-color: var(--ink-muted);
	}
	.gap {
		margin-left: 12px;
	}
	.readout {
		margin-left: auto;
	}
	.readout b {
		color: var(--ink);
	}
	.scrub {
		width: 100%;
		accent-color: var(--accent);
		margin: 0 0 6px;
	}
	.keys {
		text-transform: none;
		margin: 0 0 12px;
	}
	.stage {
		display: grid;
		grid-template-columns: minmax(0, 1fr) 240px;
		gap: 16px;
		align-items: start;
	}
	svg {
		width: 100%;
		height: min(68vh, 680px);
	}
	.track {
		fill: none;
		stroke: var(--rule);
		stroke-width: 22;
		stroke-linejoin: round;
	}
	.car circle {
		stroke: var(--bg);
		stroke-width: 3;
	}
	.car.picked circle {
		stroke: var(--ink);
		stroke-width: 4;
	}
	.car text,
	.sc text {
		font: 700 22px var(--mono);
		fill: var(--ink);
		paint-order: stroke;
		stroke: var(--bg);
		stroke-width: 6px;
	}
	.sc circle {
		fill: var(--sc);
		stroke: var(--bg);
		stroke-width: 3;
	}
	.sc .halo {
		fill: var(--sc);
		stroke: none;
		opacity: 0.25;
		animation: pulse 1.6s ease-in-out infinite;
	}
	.sc text {
		fill: var(--sc);
	}
	@keyframes pulse {
		50% {
			opacity: 0.05;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.sc .halo {
			animation: none;
		}
	}
	.dim {
		opacity: 0.2;
	}
	.tower {
		list-style: none;
		margin: 0;
		padding: 0;
		font: 13px var(--mono);
	}
	.tower li {
		border-bottom: 1px solid var(--rule-soft);
	}
	.tower button {
		width: 100%;
		display: flex;
		align-items: center;
		gap: 4px;
		padding: 4px 6px 4px 0;
		border: 0;
		border-left: 2px solid transparent;
		color: var(--ink);
		font: inherit;
		text-align: left;
	}
	.tower button[aria-pressed='true'] {
		border-left-color: var(--accent);
		background: color-mix(in srgb, var(--ink) 8%, transparent);
	}
	.pos {
		width: 2.6em;
		text-align: right;
		margin-right: 6px;
		color: var(--ink-muted);
	}
	.tyre {
		width: 10px;
		height: 10px;
		border-radius: 50%;
		margin-left: 6px;
		outline: 1px solid var(--rule);
	}
	.gap-value {
		margin-left: auto;
		color: var(--ink-muted);
		font-size: 12px;
	}
	@media (hover: hover) {
		.tower button:hover {
			background: color-mix(in srgb, var(--ink) 5%, transparent);
		}
	}
	@media (max-width: 900px) {
		.stage {
			grid-template-columns: minmax(0, 1fr);
		}
	}
</style>
