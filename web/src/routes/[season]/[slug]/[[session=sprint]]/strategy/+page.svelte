<script lang="ts">
	import Chart from '#lib/Chart.svelte';
	import { degradationOption } from '#lib/charts/degradation.ts';
	import { strategyOption } from '#lib/charts/strategy.ts';
	import { weatherOption } from '#lib/charts/weather.ts';
	import Panel from '#lib/components/Panel.svelte';
	import PitStopsTable from '#lib/components/PitStopsTable.svelte';
	import { filterPitStops, filterResults, filterStints, withLapRange } from '#lib/filters.ts';
	import { getRace } from '#lib/race.ts';
	import { tyreColor } from '#lib/tyres.ts';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const race = getRace();

	const results = $derived(filterResults(data.results, race.filters));
	const stints = $derived(filterStints(data.strategy, race.filters));
	const pitstops = $derived(filterPitStops(data.pitstops, race.filters));
	const compounds = $derived([...new Set(data.strategy.map((s) => s.cmp))]);
</script>

<div class="panels">
	<Panel title="Tyre strategies" desc="One stint per segment, in finishing order. Hover for the tyre age at the start of the stint.">
		<p class="legend">
			{#each compounds as c (c)}
				<span class="label"><span class="swatch" style:background={tyreColor(c)}></span>{c}</span>
			{/each}
		</p>
		<Chart
			option={withLapRange(
				strategyOption(stints, results, data.positions.laps, race.logos, race.filters.compounds),
				race.filters.laps
			)}
			height={results.length * 24 + 48}
		/>
	</Panel>

	<Panel
		title="Pit stops"
		desc="Official stationary time, time in the pit lane, position before the stop and after the out lap."
	>
		<PitStopsTable stops={pitstops} results={data.results} logos={race.logos} />
	</Panel>

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
			height={Math.max(160, new Set(data.degradation.map((s) => s.drv)).size * 24 + 48)}
		/>
	</Panel>

	{#if data.weather}
		<Panel
			title="Weather"
			desc="Track and air temperature through the race. Blue bands: rain. Hover for humidity and wind."
		>
			<Chart option={withLapRange(weatherOption(data.weather, data.positions.laps), race.filters.laps)} height={320} />
		</Panel>
	{/if}
</div>

<style>
	.legend {
		display: flex;
		gap: 16px;
		margin: 0 0 8px;
	}
</style>
