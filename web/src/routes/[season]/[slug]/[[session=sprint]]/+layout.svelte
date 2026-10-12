<script lang="ts">
	import { page } from '$app/state';
	import FilterBar from '#lib/components/FilterBar.svelte';
	import GpHeader from '#lib/components/GpHeader.svelte';
	import { filtersFromParams, filtersToParams, type Filters } from '#lib/filters.ts';
	import { setRace } from '#lib/race.ts';
	import { ui } from '#lib/ui.svelte.ts';
	import { readParams, writeParams } from '#lib/url.ts';
	import type { LayoutProps } from './$types';

	let { data, children }: LayoutProps = $props();

	const compounds = $derived([...new Set(data.strategy.map((s) => s.cmp))]);
	const allSelected = (): Filters => ({
		drivers: new Set(data.results.map((r) => r.drv)),
		laps: [1, data.positions.laps],
		compounds: new Set(data.strategy.map((s) => s.cmp))
	});

	let filters = $state(allSelected());
	// The layout is reused from one GP to the next: start again from "everything selected",
	// or from the filters of a shared link.
	$effect(() => {
		void data.meta.slug;
		void data.segment;
		filters = filtersFromParams(readParams(), allSelected());
	});
	// The filters live in the URL query too (?d=, l=, c=): a link brings the same view.
	$effect(() => {
		void page.url.pathname; // tab links drop the query: write it again after each one
		writeParams(filtersToParams(filters, allSelected()));
	});

	setRace({
		get filters() {
			return filters;
		},
		set filters(f) {
			filters = f;
		},
		get logos() {
			return data.logos[ui.theme];
		}
	});

	const base = $derived(`/${data.meta.season}/${data.meta.slug}${data.segment}`);
	const tabs = $derived([
		{ href: base, label: 'Overview' },
		{ href: `${base}/pace`, label: 'Pace' },
		{ href: `${base}/strategy`, label: 'Strategy' },
		{ href: `${base}/duels`, label: 'Duels' },
		{ href: `${base}/telemetry`, label: 'Telemetry' },
		{ href: `${base}/replay`, label: 'Replay' },
		{ href: `${base}/radios`, label: 'Radio', count: data.radioCount }
	]);
</script>

<svelte:head
	><title>{data.meta.name} {data.meta.season}{data.segment ? ' sprint' : ''} | OpenRoom F1</title></svelte:head
>

<main>
	<GpHeader meta={data.meta} season={data.season} laps={data.positions.laps} circuit={data.circuit}
		flag={data.meta.flag ? data.flags[data.meta.flag] : undefined}
	/>

	<div class="sticky">
		<nav class="tabs" aria-label="Grand Prix tabs">
			{#each tabs as t (t.href)}
				<a href={t.href} aria-current={page.url.pathname === t.href ? 'page' : undefined}>
					{t.label}{#if t.count !== undefined}<span class="count">{t.count}</span>{/if}
				</a>
			{/each}
		</nav>
		<FilterBar
			bind:filters
			results={data.results}
			logos={data.logos[ui.theme]}
			{compounds}
			totalLaps={data.positions.laps}
			neutral={data.events.neutral}
		/>
	</div>

	{#if filters.drivers.size === 0}
		<p class="empty label">[ NO DRIVER SELECTED ] Open the filters to pick some.</p>
	{/if}

	{@render children()}
</main>

<style>
	main {
		padding: 0 16px 24px;
		max-width: 1680px;
		margin: 0 auto;
	}
	.sticky {
		position: sticky;
		top: 0;
		z-index: 10;
		background: var(--bg);
		padding: 8px 0 12px;
		display: grid;
		gap: 8px;
	}
	.tabs {
		display: flex;
		gap: 2px;
		border-bottom: 1px solid var(--rule);
		overflow-x: auto;
	}
	.tabs a {
		font: 700 14px/1 var(--mono);
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--ink-muted);
		text-decoration: none;
		padding: 12px 18px 11px;
		border-bottom: 2px solid transparent;
		white-space: nowrap;
	}
	.tabs a[aria-current='page'] {
		color: var(--ink);
		border-bottom-color: var(--accent);
	}
	.count {
		font: 500 12px var(--mono);
		margin-left: 6px;
		color: var(--ink-muted);
	}
	@media (hover: hover) {
		.tabs a:hover {
			color: var(--ink);
		}
	}
	.empty {
		padding: 16px;
		border: 1px dashed var(--rule);
		text-transform: none;
	}
	@media (max-width: 700px) {
		.sticky {
			position: static;
		}
	}
</style>
