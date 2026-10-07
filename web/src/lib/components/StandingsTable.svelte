<script lang="ts">
	import { signed, trend } from '#lib/format.ts';
	import type { StandingRow } from '#lib/types.ts';
	import TeamMark from './TeamMark.svelte';

	let {
		rows,
		logos,
		label
	}: { rows: (StandingRow & { drv?: string })[]; logos: Record<string, string>; label: string } = $props();

	// Places gained in the championship: previous position minus current one.
	const moved = (r: StandingRow) => (r.prev === null || r.pos === null ? null : r.prev - r.pos);
</script>

<div class="scroll">
	<table class="data">
		<thead>
			<tr class="label">
				<th class="num">POS</th><th class="num">+/-</th><th>{label}</th><th class="num">PTS</th>
				<th class="num">THIS GP</th>
			</tr>
		</thead>
		<tbody>
			{#each rows as r (r.drv ?? r.team)}
				<tr>
					<td class="num">{r.pos ?? '-'}</td>
					<td class="num {trend(moved(r))}">{moved(r) ? signed(moved(r)) : ''}</td>
					<td><TeamMark src={logos[r.tid]} team={r.team} /><b>{r.drv ?? r.team}</b></td>
					<td class="num">{r.pts}</td>
					<td class="num muted">{r.gain ? `+${r.gain}` : ''}</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>
