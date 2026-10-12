<script lang="ts">
	import { miniSectors } from '#lib/telemetry.ts';
	import type { Telemetry } from '#lib/types.ts';

	let {
		tel,
		drivers,
		colors,
		count = 25
	}: { tel: Telemetry; drivers: string[]; colors: Record<string, string>; count?: number } = $props();

	const laps = $derived(drivers.map((d) => tel.laps[d]));
	const sectors = $derived(laps.length ? miniSectors(laps, count) : []);
	const points = (from: number, to: number) =>
		tel.x
			.slice(from, to + 1)
			.map((x, i) => `${x},${tel.y[from + i]}`)
			.join(' ');
	// A short bar across the track at the start of each mini-sector, perpendicular to it.
	const ticks = $derived(
		sectors.map(({ from }) => {
			const a = Math.max(from - 1, 0);
			const b = Math.min(from + 1, tel.x.length - 1);
			const dx = tel.x[b] - tel.x[a];
			const dy = tel.y[b] - tel.y[a];
			const k = 11 / (Math.hypot(dx, dy) || 1); // half length, a bit wider than the track
			return { x: tel.x[from], y: tel.y[from], nx: -dy * k, ny: dx * k };
		})
	);
	const won = $derived(drivers.map((d, i) => ({ d, n: sectors.filter((s) => s.best === i).length })));
</script>

<div class="map">
	<svg viewBox="-20 -20 {tel.w + 40} {tel.h + 40}" role="img" aria-label="Fastest driver in each mini-sector">
		<polyline class="track" points={points(0, tel.x.length - 1)} />
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
		stroke-linecap: round;
		stroke-linejoin: round;
	}
	.track {
		stroke: var(--rule);
		stroke-width: 26;
	}
	.sector {
		stroke-width: 12;
	}
	.tick {
		stroke: #0a0a0a;
		stroke-width: 3;
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
