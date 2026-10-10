<script lang="ts">
	import Chart from '#lib/Chart.svelte';
	import { qualiTimelineOption } from '#lib/charts/qualitimeline.ts';
	import DriverPicker from '#lib/components/DriverPicker.svelte';
	import Panel from '#lib/components/Panel.svelte';
	import SpeedsTable from '#lib/components/SpeedsTable.svelte';
	import { filterResults } from '#lib/filters.ts';
	import { getRace } from '#lib/race.ts';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const race = getRace();

	const results = $derived(filterResults(data.results, race.filters));
	let hidden = $state(new Set<string>());
</script>

<div class="panels">
	<Panel
		title="Flying laps"
		desc="Every flying lap against session time: the track gets faster, each run is a dot. Diamond: second driver of the team, hollow: lap deleted for track limits."
		wide
	>
		<DriverPicker {results} logos={race.logos} bind:hidden />
		<Chart
			option={qualiTimelineOption(
				data.laps,
				results.filter((r) => !hidden.has(r.drv)),
				race.logos,
				race.filters.compounds
			)}
			height={520}
		/>
	</Panel>

	<Panel
		title="Best lap, ideal lap, top speed"
		desc="Ideal lap: the driver's three best sectors of the session added up. Left: time left on the table. Red: fastest of the column."
		wide
	>
		<SpeedsTable speeds={data.speeds} {results} logos={race.logos} />
	</Panel>
</div>
