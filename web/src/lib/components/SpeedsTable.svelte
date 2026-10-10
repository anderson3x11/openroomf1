<script lang="ts">
	import { formatLap } from '#lib/stats.ts';
	import type { Driver, Speeds } from '#lib/types.ts';
	import TeamMark from './TeamMark.svelte';

	let {
		speeds,
		results,
		logos
	}: { speeds: Record<string, Speeds>; results: Driver[]; logos: Record<string, string> } = $props();

	const rows = $derived(
		results
			.filter((r) => speeds[r.drv]?.best)
			.map((r) => ({ r, s: speeds[r.drv] }))
			.sort((a, b) => (a.s.best as number) - (b.s.best as number))
	);
	// The fastest value of each column is marked, like the purple sectors on TV.
	const fastest = $derived({
		best: Math.min(...rows.map((x) => x.s.best ?? Infinity)),
		ideal: Math.min(...rows.map((x) => x.s.ideal ?? Infinity)),
		sectors: [0, 1, 2].map((i) => Math.min(...rows.map((x) => x.s.s[i] ?? Infinity))),
		top: Math.max(...rows.map((x) => x.s.top ?? 0))
	});
	const sec = (v: number | null) => (v === null ? '' : v.toFixed(3));
</script>

<div class="scroll">
	<table class="data">
		<thead>
			<tr class="label">
				<th>DRIVER</th><th class="num">BEST LAP</th><th class="num">IDEAL LAP</th>
				<th class="num" title="Time left on the table: best lap minus ideal lap">LEFT</th>
				<th class="num">S1</th><th class="num">S2</th><th class="num">S3</th>
				<th class="num" title="Speed trap">TOP KM/H</th>
			</tr>
		</thead>
		<tbody>
			{#each rows as { r, s } (r.drv)}
				<tr>
					<td><TeamMark src={logos[r.tid]} color={r.color} team={r.team} /><b>{r.drv}</b></td>
					<td class="num" class:top={s.best === fastest.best}>{formatLap(s.best as number)}</td>
					<td class="num" class:top={s.ideal === fastest.ideal}>{s.ideal ? formatLap(s.ideal) : ''}</td>
					<td class="num muted">{s.ideal && s.best ? `+${(s.best - s.ideal).toFixed(3)}` : ''}</td>
					{#each [0, 1, 2] as i (i)}
						<td class="num" class:top={s.s[i] === fastest.sectors[i]}>{sec(s.s[i])}</td>
					{/each}
					<td class="num" class:top={s.top === fastest.top}>{s.top ?? ''}</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>

<style>
	.top {
		color: var(--accent);
		font-weight: 700;
	}
</style>
