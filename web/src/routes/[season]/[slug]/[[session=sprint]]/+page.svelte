<script lang="ts">
	import Chart from '#lib/Chart.svelte';
	import { positionsOption } from '#lib/charts/positions.ts';
	import { startOption } from '#lib/charts/start.ts';
	import DriverPicker from '#lib/components/DriverPicker.svelte';
	import EventsList from '#lib/components/EventsList.svelte';
	import Highlights from '#lib/components/Highlights.svelte';
	import Panel from '#lib/components/Panel.svelte';
	import ResultsTable from '#lib/components/ResultsTable.svelte';
	import StandingsTable from '#lib/components/StandingsTable.svelte';
	import StatTiles from '#lib/components/StatTiles.svelte';
	import { filterEvents, filterResults, withLapRange } from '#lib/filters.ts';
	import { getRace } from '#lib/race.ts';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const race = getRace();

	const results = $derived(filterResults(data.results, race.filters));
	const events = $derived(filterEvents(data.events, race.filters));
	// Drivers hidden on the positions chart only, on top of the global filters.
	let hiddenPositions = $state(new Set<string>());
</script>

<StatTiles results={data.results} summary={data.summary} logos={race.logos} />

<div class="panels">
	<Panel
		title="Classification"
		desc="Official result, grid slot, places gained or lost, overtakes as counted by F1 and laps led."
		wide
	>
		<ResultsTable {results} logos={race.logos} overtakes={data.summary.overtakes} positions={data.positions} />
	</Panel>

	<Panel
		title="Lap by lap positions"
		desc="Solid line: lead finisher of the team, dashed: second driver. Yellow band: safety car or VSC."
		wide
	>
		<DriverPicker {results} logos={race.logos} bind:hidden={hiddenPositions} />
		<Chart
			option={withLapRange(
				positionsOption(
					data.positions,
					results.filter((r) => !hiddenPositions.has(r.drv)),
					race.logos,
					data.events,
					data.results
				),
				race.filters.laps
			)}
			height={560}
		/>
	</Panel>

	<Panel title="Start" desc="Places gained or lost on lap 1, from grid slot to the end of the first lap.">
		<Chart option={startOption(data.positions, results, race.logos)} height={results.length * 24 + 40} />
	</Panel>

	{#if data.race && data.meta.highlights}
		<Panel title="Race highlights" desc="Official highlights on the Formula 1 YouTube channel.">
			<Highlights
				id={data.meta.highlights}
				thumb={data.hasThumb ? `/${data.meta.season}/${data.meta.slug}/thumb.jpg` : null}
				title="{data.meta.name} {data.meta.season}"
			/>
		</Panel>
	{/if}

	<Panel
		title="Race events"
		desc="Neutralisations, flags, investigations and penalties announced by race control."
		wide
	>
		<EventsList {events} />
	</Panel>

	{#if data.standings}
		<Panel title="Championship after the GP" wide desc="Updated standings and points scored at this Grand Prix, sprint included.">
			<div class="split two">
				<StandingsTable rows={data.standings.drivers} logos={race.logos} label="DRIVER" />
				<StandingsTable rows={data.standings.teams} logos={race.logos} label="TEAM" />
			</div>
		</Panel>
	{/if}
</div>

<style>
	.split {
		display: grid;
		gap: 24px;
	}
	.two {
		grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
	}
	@media (max-width: 900px) {
		.two {
			grid-template-columns: minmax(0, 1fr);
		}
	}
</style>
