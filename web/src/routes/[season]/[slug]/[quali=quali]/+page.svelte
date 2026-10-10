<script lang="ts">
	import Panel from '#lib/components/Panel.svelte';
	import QualiTable from '#lib/components/QualiTable.svelte';
	import { filterResults } from '#lib/filters.ts';
	import { getRace } from '#lib/race.ts';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const race = getRace();
</script>

<div class="panels">
	<Panel
		title="Classification"
		desc="Best valid lap of each driver in Q1, Q2 and Q3. Red: fastest of the segment. Lines: knockouts. Gap: to the fastest time of the last segment reached."
		wide
	>
		<QualiTable rows={filterResults(data.results, race.filters)} logos={race.logos} />
	</Panel>
</div>
