<script lang="ts">
	import { signed, trend } from '#lib/format.ts';
	import type { PitStop, ResultRow } from '#lib/types.ts';
	import TeamMark from './TeamMark.svelte';

	let {
		stops,
		results,
		logos
	}: { stops: PitStop[]; results: ResultRow[]; logos: Record<string, string> } = $props();

	const byDrv = $derived(new Map(results.map((r) => [r.drv, r])));
	// Positions gained through the stop: before minus after (lower is better).
	const delta = (s: PitStop) => (s.before !== null && s.after !== null ? s.before - s.after : null);
</script>

<div class="scroll">
	<table class="data">
		<thead>
			<tr class="label">
				<th class="num">LAP</th><th>DRIVER</th><th class="num" title="Official stationary time">STOP</th>
				<th class="num">PIT LANE</th>
				<th class="num">BEFORE</th><th class="num">AFTER</th><th class="num">+/-</th><th></th>
			</tr>
		</thead>
		<tbody>
			{#each stops as s (`${s.drv}/${s.lap}`)}
				{@const r = byDrv.get(s.drv)}
				<tr>
					<td class="num">{s.lap}</td>
					<td><TeamMark src={r && logos[r.tid]} color={r?.color} team={r?.team ?? ''} /><b>{s.drv}</b></td>
					<td class="num">{s.stop === null ? '' : `${s.stop.toFixed(1)}s`}</td>
					<td class="num muted">{s.lane.toFixed(1)}s</td>
					<td class="num">{s.before ?? ''}</td>
					<td class="num">{s.after ?? ''}</td>
					<td class="num {trend(delta(s))}">{signed(delta(s))}</td>
					<td class="label">{s.under ? `[ ${s.under.toUpperCase()} ]` : ''}</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>
