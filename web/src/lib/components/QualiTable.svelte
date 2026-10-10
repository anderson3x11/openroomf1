<script lang="ts">
	import { fastestBySegment, qualiLines } from '#lib/quali.ts';
	import { formatLap } from '#lib/stats.ts';
	import type { QualiRow } from '#lib/types.ts';
	import TeamMark from './TeamMark.svelte';

	let { rows, logos }: { rows: QualiRow[]; logos: Record<string, string> } = $props();

	const lines = $derived(qualiLines(rows));
	// The fastest time of each segment is marked, like the purple sectors on TV.
	const fastest = $derived(fastestBySegment(rows));
</script>

<div class="scroll">
	<table class="data">
		<thead>
			<tr class="label">
				<th class="num">POS</th><th>DRIVER</th><th>TEAM</th>
				<th class="num">Q1</th><th class="num">Q2</th><th class="num">Q3</th>
				<th class="num" title="Gap to the fastest time of the last segment reached">GAP</th>
			</tr>
		</thead>
		<tbody>
			{#each lines as { row: r, reached, gap, cut } (r.drv)}
				<tr class:cut>
					<td class="num">{r.pos}</td>
					<td><TeamMark src={logos[r.tid]} color={r.color} team={r.team} /><b>{r.drv}</b> {r.name}</td>
					<td class="muted">{r.team}</td>
					{#each r.q as t, i (i)}
						<td class="num" class:top={t !== null && t === fastest[i]} class:muted={i < reached}
							>{t === null ? '' : formatLap(t)}</td
						>
					{/each}
					<td class="num muted">{gap ? `+${gap.toFixed(3)}` : ''}</td>
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
	/* Knockout line: the first driver out of a segment. */
	.cut td {
		border-top: 2px solid var(--ink-muted); /* wider than the row rule, or the collapse hides it */
	}
</style>
