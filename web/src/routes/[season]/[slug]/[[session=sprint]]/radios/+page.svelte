<script lang="ts">
	import Panel from '#lib/components/Panel.svelte';
	import TeamMark from '#lib/components/TeamMark.svelte';
	import { inLaps } from '#lib/filters.ts';
	import { getRace } from '#lib/race.ts';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const race = getRace();

	const byDrv = $derived(new Map(data.results.map((r) => [r.drv, r])));
	// Radios without a known lap, or before the start, are kept whatever the lap range.
	const radios = $derived(
		data.radios.filter(
			(r) => race.filters.drivers.has(r.drv) && (r.lap === null || r.lap === 0 || inLaps(r.lap, race.filters.laps))
		)
	);
	const lapLabel = (lap: number | null) => (lap === null ? '-' : lap === 0 ? 'PRE' : `L${lap}`);
</script>

<div class="panels">
	<Panel
		title="Team radio"
		desc="Messages broadcast during the race, placed on the driver's lap. Audio plays from the official F1 server."
		wide
	>
		{#if data.radios.length === 0}
			<p class="label">[ NO RADIO ] None published for this Grand Prix.</p>
		{:else}
			<div class="scroll">
				<table class="data">
					<thead>
						<tr class="label">
							<th class="num">LAP</th><th>TIME UTC</th><th>DRIVER</th><th>AUDIO</th>
						</tr>
					</thead>
					<tbody>
						{#each radios as r (r.url)}
							{@const d = byDrv.get(r.drv)}
							<tr>
								<td class="num">{lapLabel(r.lap)}</td>
								<td class="muted">{r.at}</td>
								<td><TeamMark src={d && race.logos[d.tid]} color={d?.color} team={d?.team ?? ''} /><b>{r.drv}</b></td>
								<td><audio controls preload="none" src={r.url}></audio></td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	</Panel>
</div>

<style>
	audio {
		height: 32px;
		width: 260px;
		vertical-align: middle;
	}
</style>
