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
		<dt class="label">[ {label} ]</dt>
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
		overtaker ? `${byDrv.get(overtaker[0])?.name ?? ''}, official F1 data` : ''
	)}
</dl>

<style>
	.tiles {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
		gap: 1px;
		background: var(--rule);
		border: 1px solid var(--rule);
		margin: 0 0 16px;
	}
	.tiles > div {
		background: var(--bg);
		padding: 18px 20px;
	}
	dt {
		color: var(--ink-muted);
	}
	dd {
		margin: 0;
	}
	.big {
		font: 700 34px/1.1 var(--mono);
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
	.value {
		margin-left: auto;
		color: var(--ink);
	}
	.sub {
		font: 13px var(--mono);
		color: var(--ink-muted);
	}
</style>
