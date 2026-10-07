<script lang="ts">
	import { signed, trend } from '#lib/format.ts';
	import type { Positions, ResultRow } from '#lib/types.ts';
	import TeamMark from './TeamMark.svelte';

	let {
		results,
		logos,
		overtakes,
		positions
	}: {
		results: ResultRow[];
		logos: Record<string, string>;
		overtakes: Record<string, number>;
		positions: Positions;
	} = $props();

	// Laps led: laps completed in P1 (lap 0 is the grid).
	const led = (drv: string) => (positions.pos[drv] ?? []).filter((p, lap) => lap > 0 && p === 1).length;
</script>

<div class="scroll">
	<table class="data">
		<thead>
			<tr class="label">
				<th class="num">POS</th><th>DRIVER</th><th>TEAM</th><th class="num">GRID</th>
				<th class="num">+/-</th><th class="num" title="Overtakes, official F1 data">OVT</th>
				<th class="num" title="Laps led">LED</th><th class="num">PTS</th><th>STATUS</th>
			</tr>
		</thead>
		<tbody>
			{#each results as r (r.drv)}
				<tr>
					<td class="num">{r.cls}</td>
					<td><TeamMark src={logos[r.tid]} color={r.color} team={r.team} /><b>{r.drv}</b> {r.name}</td>
					<td class="muted">{r.team}</td>
					<td class="num">{r.grid ?? 'PIT'}</td>
					<td class="num {trend(r.gain)}">{signed(r.gain)}</td>
					<td class="num">{overtakes[r.drv] || ''}</td>
					<td class="num">{led(r.drv) || ''}</td>
					<td class="num">{r.pts || ''}</td>
					<td class="muted">{r.status}</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>
