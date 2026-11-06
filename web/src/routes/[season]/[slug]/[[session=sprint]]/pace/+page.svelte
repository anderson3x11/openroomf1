<script lang="ts">
	import Chart from '#lib/Chart.svelte';
	import { gapsOption } from '#lib/charts/gaps.ts';
	import { heatmapOption } from '#lib/charts/heatmap.ts';
	import { raceTraceOption } from '#lib/charts/racetrace.ts';
	import { laptimesOption } from '#lib/charts/laptimes.ts';
	import Panel from '#lib/components/Panel.svelte';
	import SpeedsTable from '#lib/components/SpeedsTable.svelte';
	import { filterLapTimes, filterResults, withLapRange } from '#lib/filters.ts';
	import { getRace } from '#lib/race.ts';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const race = getRace();

	const results = $derived(filterResults(data.results, race.filters));
	const laptimes = $derived(filterLapTimes(data.laptimes, data.strategy, race.filters));
	// '' = gap to the leader of each lap, else gap to this driver (undercuts, pit windows).
	let ref = $state('');
</script>

<div class="panels">
	<Panel
		title="Race trace"
		desc="Time gained (+) or lost (-) against a typical car that laps, every lap, in the median lap time of the field. Rising: faster than the field, falling: slower, sharp drops: pit stops. Rain and safety cars slow the reference down too. Mouse wheel or right slider to zoom."
		wide
	>
		<Chart
			option={withLapRange(
				raceTraceOption(data.raceTrace, results, race.logos, data.events, data.results),
				race.filters.laps
			)}
			height={680}
		/>
	</Panel>

	<Panel
		title={ref ? `Gap to ${ref}` : 'Gap to leader'}
		desc={ref
			? `Negative: ahead of ${ref}, positive: behind. Mouse wheel or right slider to zoom.`
			: 'Time behind the first driver to complete each lap. Mouse wheel or right slider to zoom.'}
		wide
	>
		{#snippet actions()}
			<label class="label"
				>REFERENCE
				<select bind:value={ref}>
					<option value="">LEADER</option>
					{#each data.results as r (r.drv)}
						<option value={r.drv}>{r.drv} / {r.name}</option>
					{/each}
				</select>
			</label>
		{/snippet}
		<Chart
			option={withLapRange(
				gapsOption(data.gaps, results, race.logos, data.events, ref, data.results),
				race.filters.laps
			)}
			height={680}
		/>
	</Panel>

	<Panel
		title="Lap time heatmap"
		desc="Every lap of every driver, colored by the time lost to the fastest clean lap of the race. Gray: pit laps and laps under SC or VSC."
		wide
	>
		<Chart
			option={heatmapOption(data.lapMatrix, results, race.logos, race.filters.laps)}
			height={results.length * 30 + 80}
		/>
	</Panel>

	<Panel
		title="Lap time distribution"
		desc="Representative laps only: no lap 1, no pit laps, no laps under SC or VSC. Sorted from fastest to slowest median pace."
		wide
	>
		<Chart
			option={laptimesOption(laptimes, data.results, race.logos)}
			height={Object.keys(laptimes).length * 32 + 48}
		/>
	</Panel>

	<Panel
		title="Best lap, ideal lap and top speed"
		desc="Ideal lap: the driver's three best sectors put together. Left: time between it and his best lap. Top speed through the speed trap. The fastest of each column is in red."
		wide
	>
		<SpeedsTable speeds={data.speeds} {results} logos={race.logos} />
	</Panel>
</div>

<style>
	select {
		font: 500 13px var(--mono);
		color: var(--ink);
		background: var(--bg);
		border: 1px solid var(--rule);
		padding: 5px 8px;
		margin-left: 8px;
		text-transform: uppercase;
	}
</style>
