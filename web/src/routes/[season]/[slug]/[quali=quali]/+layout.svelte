<script lang="ts">
	import { page } from '$app/state';
	import FilterBar from '#lib/components/FilterBar.svelte';
	import GpHeader from '#lib/components/GpHeader.svelte';
	import { filtersFromParams, filtersToParams, type Filters } from '#lib/filters.ts';
	import { SESSION_LABELS } from '#lib/format.ts';
	import { setRace } from '#lib/race.ts';
	import { ui } from '#lib/ui.svelte.ts';
	import { readParams, writeParams } from '#lib/url.ts';
	import type { LayoutProps } from './$types';

	let { data, children }: LayoutProps = $props();

	const compounds = $derived([
		...new Set(Object.values(data.laps.laps).flatMap((laps) => laps.map(([, , , cmp]) => cmp)))
	]);
	// No lap range in qualifying: laps stays at its default and the filter bar hides it.
	const allSelected = (): Filters => ({
		drivers: new Set(data.results.map((r) => r.drv)),
		laps: [1, 1],
		compounds: new Set(compounds)
	});

	let filters = $state(allSelected());
	$effect(() => {
		void data.meta.slug;
		void data.session;
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

	const base = $derived(`/${data.meta.season}/${data.meta.slug}/${data.session}`);
	const tabs = $derived([
		{ href: base, label: 'Classification' },
		{ href: `${base}/pace`, label: 'Pace' },
		{ href: `${base}/telemetry`, label: 'Telemetry' }
	]);
</script>

<svelte:head
	><title>{data.meta.name} {data.meta.season} {SESSION_LABELS[data.session].toLowerCase()} | OpenRoom F1</title
	></svelte:head
>

<main>
	<GpHeader meta={data.meta} season={data.season} circuit={data.circuit}
		flag={data.meta.flag ? data.flags[data.meta.flag] : undefined}
	/>

	<div class="sticky">
		<nav class="tabs" aria-label="{SESSION_LABELS[data.session]} tabs">
			{#each tabs as t (t.href)}
				<a href={t.href} aria-current={page.url.pathname === t.href ? 'page' : undefined}>{t.label}</a>
			{/each}
		</nav>
		<FilterBar bind:filters results={data.results} logos={data.logos[ui.theme]} {compounds} />
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
