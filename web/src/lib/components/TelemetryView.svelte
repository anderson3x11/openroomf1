<script lang="ts">
	import Chart from '#lib/Chart.svelte';
	import { telemetryHeight, telemetryOption } from '#lib/charts/telemetry.ts';
	import { formatLap } from '#lib/stats.ts';
	import { distinctColors } from '#lib/telemetry.ts';
	import type { Driver, Telemetry } from '#lib/types.ts';
	import { readParams, writeParams } from '#lib/url.ts';
	import DominationMap from './DominationMap.svelte';
	import Panel from './Panel.svelte';
	import TeamMark from './TeamMark.svelte';

	let {
		url,
		results,
		logos
	}: { url: string; results: Driver[]; logos: Record<string, string> } = $props();

	const MAX = 4;

	// Fetched on demand, like the replay: about 300 KB per session.
	let tel = $state<Telemetry | null>(null);
	let failed = $state(false);
	let selected = $state<string[]>([]);

	$effect(() => {
		tel = null;
		failed = false;
		fetch(url)
			.then((r) => r.json())
			.then((t: Telemetry | null) => {
				tel = t;
				failed = t === null;
				if (!t) return;
				// From the shared link (?drv=VER,LEC), else the two fastest laps.
				const wanted = (readParams().get('drv') ?? '').split(',').filter((d) => t.laps[d]);
				selected = (wanted.length ? wanted : Object.keys(t.laps).slice(0, 2)).slice(0, MAX);
			})
			.catch(() => (failed = true));
	});
	$effect(() => {
		if (tel) writeParams({ drv: selected.join(',') || null });
	});

	// Drivers with a lap, in classification order.
	const available = $derived(tel ? results.filter((r) => tel?.laps[r.drv]) : []);
	const byDrv = $derived(new Map(results.map((r) => [r.drv, r])));
	const colors = $derived(distinctColors(selected.map((d) => byDrv.get(d)).filter((r): r is Driver => !!r)));

	function toggle(drv: string) {
		if (selected.includes(drv)) selected = selected.filter((d) => d !== drv);
		else selected = [...selected, drv].slice(-MAX); // the oldest choice makes room
	}
	const setRef = (drv: string) => (selected = [drv, ...selected.filter((d) => d !== drv)]);
</script>

{#if failed}
	<p class="label empty">[ NO TELEMETRY ] FastF1 has no car data for this session.</p>
{:else if !tel}
	<p class="label empty">[ LOADING TELEMETRY ]</p>
{:else}
	<div class="panels">
		<Panel
			title="Best laps compared"
			desc="Pick up to {MAX} drivers. The first one is the reference of the delta: above zero, time lost to him. Mouse wheel or bottom slider to zoom on a corner. The link keeps the drivers chosen."
			wide
		>
			<div class="picker">
				{#each available as r (r.drv)}
					<button
						class="chip"
						aria-pressed={selected.includes(r.drv)}
						style:--team={colors[r.drv] ?? r.color}
						title={r.name}
						onclick={() => toggle(r.drv)}><TeamMark src={logos[r.tid]} color={r.color} team={r.team} />{r.drv}</button
					>
				{/each}
			</div>
			{#if selected.length}
				<div class="scroll">
					<table class="data">
						<thead>
							<tr class="label">
								<th>DRIVER</th><th class="num">LAP</th><th class="num">TIME</th><th class="num">GAP</th><th>TYRE</th><th></th>
							</tr>
						</thead>
						<tbody>
							{#each selected as d, i (d)}
								{@const lap = tel.laps[d]}
								<tr>
									<td><span class="swatch" style:background={colors[d]}></span><b>{d}</b> {byDrv.get(d)?.name ?? ''}</td>
									<td class="num">{lap.lap}</td>
									<td class="num">{formatLap(lap.time)}</td>
									<td class="num muted">{i ? `+${(lap.time - tel.laps[selected[0]].time).toFixed(3)}` : 'REF'}</td>
									<td class="muted">{lap.cmp}</td>
									<td>{#if i}<button class="label link" onclick={() => setRef(d)}>[ SET AS REF ]</button>{/if}</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
				<Chart option={telemetryOption(tel, selected, colors)} height={telemetryHeight(tel, selected)} />
			{/if}
		</Panel>

		{#if selected.length > 1}
			<Panel
				title="Track domination"
				desc="The lap cut into 25 mini-sectors of equal length, each colored with the fastest driver through it."
				wide
			>
				<DominationMap {tel} drivers={selected} {colors} />
			</Panel>
		{/if}
	</div>
{/if}

<style>
	.empty {
		padding: 16px;
		border: 1px dashed var(--rule);
	}
	.picker {
		display: flex;
		flex-wrap: wrap;
		gap: 4px;
		margin-bottom: 12px;
	}
	.chip {
		display: inline-flex;
		align-items: center;
		gap: 6px;
		font: 700 12px var(--mono);
		color: var(--ink-muted);
		background: none;
		border: 1px solid var(--rule);
		border-left: 3px solid var(--rule);
		padding: 4px 8px;
		cursor: pointer;
	}
	.chip[aria-pressed='true'] {
		color: var(--ink);
		border-left-color: var(--team);
		background: var(--panel);
	}
	.link {
		background: none;
		border: none;
		cursor: pointer;
		padding: 0;
	}
	table {
		margin-bottom: 12px;
	}
</style>
