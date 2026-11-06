<script lang="ts">
		import { formatLap } from '#lib/stats.ts';
	import type { ResultRow, Summary } from '#lib/types.ts';
	import TeamMark from './TeamMark.svelte';

	let {
		results,
		summary,
		logos
	}: { results: ResultRow[]; summary: Summary; logos: Record<string, string> } = $props();

	const byDrv = $derived(new Map(results.map((r) => [r.drv, r])));
	const pole = $derived(results.find((r) => r.grid === 1));
	const winner = $derived(results[0]);
	const fastest = $derived(summary.fastest);
	const overtaker = $derived(
		Object.entries(summary.overtakes).reduce<[string, number] | undefined>(
			(best, cur) => (cur[1] > (best?.[1] ?? 0) ? cur : best),
			undefined
		)
	);
</script>

{#snippet who(drv: string)}
	{@const r = byDrv.get(drv)}
	<TeamMark src={r && logos[r.tid]} color={r?.color} team={r?.team ?? ''} /><b>{drv}</b>
{/snippet}

{#snippet tile(label: string, drv: string | undefined, value: string, sub: string)}
	<div>
		<dt class="label">{label}</dt>
		{#if drv}
			<dd class="big">{@render who(drv)}<span class="value">{value}</span></dd>
			<dd class="sub">{sub}</dd>
		{:else}
			<dd class="big">-</dd>
		{/if}
	</div>
{/snippet}

<dl class="tiles">
	{@render tile('Pole position', pole?.drv, '', pole ? `${pole.name}, finished P${pole.cls}` : '')}
	{@render tile('Winner', winner?.drv, '', winner ? `${winner.name}, started P${winner.grid ?? 'IT'}` : '')}
	{@render tile(
		'Fastest lap',
		fastest?.drv,
		fastest ? formatLap(fastest.t) : '',
		fastest ? `${byDrv.get(fastest.drv)?.name ?? ''}, lap ${fastest.lap}` : ''
	)}
	{@render tile(
		'Most overtakes',
		overtaker?.[0],
		overtaker ? String(overtaker[1]) : '',
		overtaker ? `${byDrv.get(overtaker[0])?.name ?? ''}, F1 timing data` : ''
	)}
</dl>

<style>
	.tiles {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: var(--gap);
		margin: 0 0 var(--gap);
	}
	.tiles > div {
		background: var(--panel);
		border-radius: var(--radius);
		padding: 18px 20px;
	}
	/* The race's one fact, in the color of the page. */
	.tiles > div:nth-child(2) {
		color: var(--on-accent);
		background: var(--accent);
	}
	.tiles > div:nth-child(2) :is(dt, .sub) {
		color: inherit;
	}
	dt {
		color: var(--ink-muted);
	}
	dd {
		margin: 0;
	}
	.big {
		font: 700 27px/1.1 var(--sans);
		margin: 12px 0 6px;
		display: flex;
		align-items: center;
		gap: 4px;
	}
	.big :global(img) {
		height: 32px;
		width: 32px;
		margin-right: 12px;
	}
	/* Logos are chosen for the panels of the theme: on red, they keep a disc of that color. */
	.tiles > div:nth-child(2) .big :global(img) {
		box-sizing: content-box;
		padding: 6px;
		margin: -6px 8px -6px 0;
		background: var(--panel);
		border-radius: 50%;
	}
	.value {
		margin-left: auto;
		padding-left: 12px;
		font: 700 24px/1.1 var(--mono); /* the display font has no real colon for lap times */
		color: var(--ink);
	}
	.sub {
		font: 13px var(--mono);
		color: var(--ink-muted);
	}
	@media (min-width: 1500px) {
		.tiles {
			grid-template-columns: repeat(4, minmax(0, 1fr));
		}
	}
	@media (max-width: 700px) {
		.tiles {
			grid-template-columns: minmax(0, 1fr);
		}
	}
</style>
