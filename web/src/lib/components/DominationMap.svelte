<script lang="ts">
	import { miniSectors, smooth } from '#lib/telemetry.ts';
	import type { Telemetry } from '#lib/types.ts';

	let {
		tel,
		drivers,
		colors,
		count = 25
	}: { tel: Telemetry; drivers: string[]; colors: Record<string, string>; count?: number } = $props();

	const laps = $derived(drivers.map((d) => tel.laps[d]));
	const sectors = $derived(laps.length ? miniSectors(laps, count) : []);
	// Smoothed over about 50 m: the raw positions come from GPS, every 10 m.
	const xs = $derived(smooth(tel.x, 2));
	const ys = $derived(smooth(tel.y, 2));
	const points = (from: number, to: number) =>
		xs
			.slice(from, to + 1)
			.map((x, i) => `${x.toFixed(1)},${ys[from + i].toFixed(1)}`)
			.join(' ');
	// A short bar across the track at the start of each mini-sector, perpendicular to it.
	const ticks = $derived(
		sectors.map(({ from }) => {
			// Direction over 60 m around the boundary: steadier than two neighbouring points.
			const a = Math.max(from - 3, 0);
			const b = Math.min(from + 3, xs.length - 1);
			const dx = xs[b] - xs[a];
			const dy = ys[b] - ys[a];
			const k = 8 / (Math.hypot(dx, dy) || 1); // half length, just wider than the track
			return { x: xs[from], y: ys[from], nx: -dy * k, ny: dx * k };
		})
	);
	const won = $derived(drivers.map((d, i) => ({ d, n: sectors.filter((s) => s.best === i).length })));
</script>

<div class="map">
	<svg viewBox="-20 -20 {tel.w + 40} {tel.h + 40}" role="img" aria-label="Fastest driver in each mini-sector">
		<polyline class="track" points={points(0, xs.length - 1)} />
		{#each sectors as s, k (k)}
			<polyline class="sector" points={points(s.from, s.to)} style:stroke={colors[drivers[s.best]]} />
		{/each}
		{#each ticks as t, k (k)}
			<line class="tick" x1={t.x - t.nx} y1={t.y - t.ny} x2={t.x + t.nx} y2={t.y + t.ny} />
		{/each}
	</svg>
	<ul class="label">
		{#each won as { d, n } (d)}
			<li><span class="swatch" style:background={colors[d]}></span><b>{d}</b> {n}/{count}</li>
		{/each}
	</ul>
</div>

<style>
	.map {
		display: grid;
		gap: 12px;
	}
	svg {
		width: 100%;
		max-height: 520px;
	}
	polyline {
		fill: none;
		stroke-linejoin: round;
	}
	.track {
		stroke: var(--rule);
		stroke-width: 14;
		stroke-linecap: round;
	}
	/* Square ends: a round cap would spill over the next mini-sector. */
	.sector {
		stroke-width: 8;
		stroke-linecap: butt;
	}
	.tick {
		stroke: #0a0a0a;
		stroke-width: 2.5;
	}
	ul {
		list-style: none;
		margin: 0;
		padding: 0;
		display: flex;
		flex-wrap: wrap;
		gap: 16px;
	}
	b {
		color: var(--ink);
	}
</style>
