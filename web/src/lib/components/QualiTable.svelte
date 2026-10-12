<script lang="ts">
	import { fastestBySegment, qualiLines } from '#lib/quali.ts';
	import { formatLap } from '#lib/stats.ts';
	import type { QualiRow } from '#lib/types.ts';
	import TeamMark from './TeamMark.svelte';

	let { rows, logos }: { rows: QualiRow[]; logos: Record<string, string> } = $props();

	const lines = $derived(qualiLines(rows));
	// The fastest time of each segment is marked, like the purple sectors on TV.
	const fastest = $derived(fastestBySegment(rows));
	// Free practice is a single segment: its column is the best lap.
	const columns = $derived((rows[0]?.q.length ?? 3) === 1 ? ['BEST'] : ['Q1', 'Q2', 'Q3']);
</script>

<div class="scroll">
	<table class="data">
		<thead>
			<tr class="label">
				<th class="num">POS</th><th>DRIVER</th><th>TEAM</th>
				{#each columns as c (c)}<th class="num">{c}</th>{/each}
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
