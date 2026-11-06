<script lang="ts">
	import Chart from '#lib/Chart.svelte';
	import { degradationOption } from '#lib/charts/degradation.ts';
	import { weatherOption } from '#lib/charts/weather.ts';
	import Panel from '#lib/components/Panel.svelte';
	import PitStopsTable from '#lib/components/PitStopsTable.svelte';
	import StrategyChart from '#lib/components/StrategyChart.svelte';
	import { filterPitStops, filterResults, filterStints, withLapRange } from '#lib/filters.ts';
	import { getRace } from '#lib/race.ts';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const race = getRace();

	const results = $derived(filterResults(data.results, race.filters));
	const stints = $derived(filterStints(data.strategy, race.filters));
	const pitstops = $derived(filterPitStops(data.pitstops, race.filters));
	const compounds = $derived([...new Set(data.strategy.map((s) => s.cmp))]);
</script>

<div class="panels">
	<Panel
		title="Tyre strategies"
		desc="One line per driver in finishing order, one color per compound. Discs: lap of each pit stop, on the right: last lap. Hover a stint for its tyre age."
		wide
	>
		<StrategyChart
			drivers={results}
			{stints}
			laps={race.filters.laps}
			compounds={race.filters.compounds}
			legend={compounds}
			stops={pitstops.length}
		/>
	</Panel>

	<Panel
		title="Pit stops"
		desc="Time in the pit lane, position before the stop and after the out lap. Official stationary time when the data has it."
	>
		<PitStopsTable stops={pitstops} results={data.results} logos={race.logos} />
	</Panel>

	<div class="side">
		<Panel
			title="Tyre degradation"
			desc="Lap time lost per lap of tyre age, one dot per stint, corrected for fuel burn (0.03 s per lap). Clean laps only: no pit laps, no SC or VSC, not the first two laps of the stint."
		>
			<Chart
				option={degradationOption(
					data.degradation.filter((s) => race.filters.compounds.has(s.cmp)),
					results,
					race.logos
				)}
				height={Math.max(160, new Set(data.degradation.map((s) => s.drv)).size * 30 + 48)}
			/>
		</Panel>

		{#if data.weather}
			<Panel
				title="Weather"
				desc="Track and air temperature through the race. Blue bands: rain. Hover for humidity and wind."
			>
				<Chart option={withLapRange(weatherOption(data.weather, data.positions.laps), race.filters.laps)} height={380} />
			</Panel>
		{/if}
	</div>
</div>

<style>
	.side {
		display: grid;
		gap: var(--gap);
		min-width: 0;
		align-content: start;
	}
	@media (min-width: 1401px) {
		.side {
			position: sticky;
			top: 66px;
			align-self: start;
		}
	}
</style>

