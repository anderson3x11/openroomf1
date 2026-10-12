<script lang="ts">
	import TelemetryView from '#lib/components/TelemetryView.svelte';
	import { filterResults } from '#lib/filters.ts';
	import { getRace } from '#lib/race.ts';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const race = getRace();
</script>

<TelemetryView
	url="/{data.meta.season}/{data.meta.slug}/{data.session}/telemetry.json"
	results={filterResults(data.results, race.filters)}
	logos={race.logos}
/>
