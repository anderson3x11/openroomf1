<script lang="ts">
	// Per chart driver selection, on top of the global filters. It stands in for the chart
	// legend: team color, logo and code for every line.
	import type { Driver } from '#lib/types.ts';
	import TeamMark from './TeamMark.svelte';

	let {
		results,
		logos,
		hidden = $bindable()
	}: { results: Driver[]; logos: Record<string, string>; hidden: Set<string> } = $props();

	const all = $derived(results.map((r) => r.drv));
	// Sets are replaced, not mutated, so that Svelte sees the change.
	function toggle(drv: string) {
		const next = new Set(hidden);
		if (next.has(drv)) next.delete(drv);
		else next.add(drv);
		hidden = next;
	}
	// Double click isolates: the two clicks before it toggle twice, so they cancel out.
	const isolate = (drv: string) => (hidden = new Set(all.filter((d) => d !== drv)));
</script>

<div class="picker" role="group" aria-label="Drivers shown on this chart">
	<button class="label link" onclick={() => (hidden = new Set())}>[ ALL ]</button>
	<button class="label link" onclick={() => (hidden = new Set(all))}>[ NONE ]</button>
	{#each results as r (r.drv)}
		<button
			class="chip"
			style:--team={r.color}
			aria-pressed={!hidden.has(r.drv)}
			title="{r.name}: click to show or hide, double click to isolate"
			onclick={() => toggle(r.drv)}
			ondblclick={() => isolate(r.drv)}
		>
			<TeamMark src={logos[r.tid]} color={r.color} team={r.team} />{r.drv}
		</button>
	{/each}
</div>

<style>
	.picker {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 4px;
		margin-bottom: 10px;
	}
	button {
		font: 500 12px/1 var(--mono);
		letter-spacing: 0.04em;
		color: var(--ink-muted);
		background: none;
		border: 0;
		cursor: pointer;
		touch-action: manipulation;
		user-select: none;
	}
	.link {
		padding: 4px 4px 4px 0;
	}
	.chip {
		display: inline-flex;
		align-items: center;
		padding: 4px 7px 4px 5px;
		border: 1px solid var(--rule);
		border-left: 3px solid var(--team, var(--rule));
		opacity: 0.35;
	}
	.chip[aria-pressed='true'] {
		color: var(--ink);
		opacity: 1;
	}
	.chip :global(img) {
		height: 14px;
		width: 14px;
		margin-right: 4px;
		vertical-align: 0;
	}
	@media (hover: hover) {
		button:hover {
			color: var(--ink);
			opacity: 1;
		}
	}
</style>
