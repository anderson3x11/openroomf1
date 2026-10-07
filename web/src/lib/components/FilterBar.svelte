<script lang="ts">
	import type { Filters } from '#lib/filters.ts';
	import { tyreColor } from '#lib/tyres.ts';
	import type { RaceEvents, ResultRow } from '#lib/types.ts';
	import LapStrip from './LapStrip.svelte';
	import TeamMark from './TeamMark.svelte';

	let {
		filters = $bindable(),
		results,
		logos,
		compounds,
		totalLaps,
		neutral
	}: {
		filters: Filters;
		results: ResultRow[];
		logos: Record<string, string>;
		compounds: string[];
		totalLaps: number;
		neutral: RaceEvents['neutral'];
	} = $props();

	let open = $state(false);

	// Teams in finishing order of their best driver, each with its drivers.
	const teams = $derived(
		[...new Map(results.map((r) => [r.team, r])).values()].map((t) => ({
			...t,
			drivers: results.filter((r) => r.team === t.team)
		}))
	);
	const allDrivers = $derived(results.map((r) => r.drv));

	// Sets are replaced, not mutated, so that Svelte sees the change.
	function toggle(drivers: string[]) {
		const next = new Set(filters.drivers);
		const allOn = drivers.every((d) => next.has(d));
		for (const d of drivers) {
			if (allOn) next.delete(d);
			else next.add(d);
		}
		filters = { ...filters, drivers: next };
	}
	// Double click isolates: the two clicks before it toggle twice, so they cancel out.
	const setDrivers = (drivers: string[]) => (filters = { ...filters, drivers: new Set(drivers) });

	function toggleCompound(c: string) {
		const next = new Set(filters.compounds);
		if (next.has(c)) next.delete(c);
		else next.add(c);
		filters = { ...filters, compounds: next };
	}

	function setLap(index: 0 | 1, value: number) {
		const laps: [number, number] = [...filters.laps];
		laps[index] = Math.min(Math.max(Math.round(value) || 1, 1), totalLaps);
		if (laps[0] > laps[1]) laps[1 - index] = laps[index];
		filters = { ...filters, laps };
	}

	function reset() {
		filters = { drivers: new Set(allDrivers), laps: [1, totalLaps], compounds: new Set(compounds) };
	}

	const isDefault = $derived(
		filters.drivers.size === allDrivers.length &&
			filters.laps[0] === 1 &&
			filters.laps[1] === totalLaps &&
			filters.compounds.size === compounds.length
	);
</script>

<div class="filters">
	<div class="summary">
		<button class="label toggle" aria-expanded={open} onclick={() => (open = !open)}>
			[ FILTERS {open ? '-' : '+'} ]
		</button>
		<span class="label state">
			<b>{filters.drivers.size}/{allDrivers.length}</b> DRIVERS
			<span aria-hidden="true">/</span> LAPS <b>{filters.laps[0]}-{filters.laps[1]}</b>
			<span aria-hidden="true">/</span> TYRES <b>{filters.compounds.size}/{compounds.length}</b>
		</span>
		{#if !isDefault}
			<button class="label link" onclick={reset}>[ RESET ]</button>
		{/if}
	</div>

	{#if open}
		<div class="body">
			<div class="row">
				<span class="label title">DRIVERS</span>
				<button class="label link" onclick={() => setDrivers(allDrivers)}>[ ALL ]</button>
				<button class="label link" onclick={() => setDrivers([])}>[ NONE ]</button>
				<span class="hint">
					Click: add or remove. Double click: isolate. Logo: whole team.
				</span>
			</div>
			<div class="teams">
				{#each teams as t (t.team)}
					{@const drvs = t.drivers.map((d) => d.drv)}
					<div class="team" style:--team={t.color}>
						<button
							class="logo"
							title={t.team}
							aria-label="Team {t.team}"
							aria-pressed={drvs.every((d) => filters.drivers.has(d))}
							onclick={() => toggle(drvs)}
							ondblclick={() => setDrivers(drvs)}
						>
							<TeamMark src={logos[t.tid]} color={t.color} team={t.team} />
						</button>
						{#each t.drivers as d (d.drv)}
							<button
								class="chip"
								aria-pressed={filters.drivers.has(d.drv)}
								title={d.name}
								onclick={() => toggle([d.drv])}
								ondblclick={() => setDrivers([d.drv])}>{d.drv}</button
							>
						{/each}
					</div>
				{/each}
			</div>
			<div class="row">
				<span class="label title">LAPS</span>
				<label class="label"
					>FROM <input
						type="number"
						min="1"
						max={totalLaps}
						value={filters.laps[0]}
						onchange={(e) => setLap(0, e.currentTarget.valueAsNumber)}
					/></label
				>
				<label class="label"
					>TO <input
						type="number"
						min="1"
						max={totalLaps}
						value={filters.laps[1]}
						onchange={(e) => setLap(1, e.currentTarget.valueAsNumber)}
					/></label
				>
				<button class="label link" onclick={() => (filters = { ...filters, laps: [1, totalLaps] })}
					>[ ALL LAPS ]</button
				>
			</div>
			<div class="laps">
				<LapStrip bind:laps={() => filters.laps, (laps) => (filters = { ...filters, laps })} total={totalLaps} {neutral} />
				<span class="hint">Drag across laps to pick a range, click one lap to isolate it. Yellow: SC or VSC.</span>
			</div>
			<div class="row">
				<span class="label title">TYRES</span>
				{#each compounds as c (c)}
					<button class="chip boxed" aria-pressed={filters.compounds.has(c)} onclick={() => toggleCompound(c)}>
						<span class="swatch" style:background={tyreColor(c)}></span>{c}
					</button>
				{/each}
			</div>
		</div>
	{/if}
</div>

<style>
	.filters {
		border: 1px solid var(--rule);
		background: var(--panel);
	}
	.summary {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: 12px;
		padding: 10px 14px;
	}
	.state b {
		color: var(--ink);
		font-weight: 700;
	}
	.body {
		display: grid;
		gap: 10px;
		padding: 4px 12px 12px;
		border-top: 1px solid var(--rule-soft);
	}
	.row {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 8px;
		padding-top: 8px;
	}
	.title {
		color: var(--ink);
		min-width: 5.5em;
	}
	.hint {
		font: 12px var(--mono);
		color: var(--ink-muted);
	}
	.laps {
		display: grid;
		gap: 2px;
	}
	.teams {
		display: flex;
		flex-wrap: wrap;
		gap: 6px;
	}
	.team {
		display: flex;
		align-items: stretch;
		border: 1px solid var(--rule);
		border-left: 3px solid var(--team, var(--rule));
	}
	button {
		font: 500 13px/1 var(--mono);
		letter-spacing: 0.04em;
		color: var(--ink-muted);
		background: none;
		border: 0;
		cursor: pointer;
		touch-action: manipulation;
		user-select: none;
	}
	.toggle {
		color: var(--ink);
		padding: 2px 0;
	}
	.link {
		padding: 2px 0;
	}
	.chip,
	.logo {
		padding: 7px 9px;
		display: inline-flex;
		align-items: center;
		opacity: 0.4;
	}
	.team .chip {
		border-left: 1px solid var(--rule-soft);
	}
	.boxed {
		border: 1px solid var(--rule);
	}
	[aria-pressed='true'] {
		opacity: 1;
		color: var(--ink);
	}
	.chip[aria-pressed='true'] {
		background: color-mix(in srgb, var(--focus) 10%, transparent);
	}
	.logo :global(img) {
		margin: 0;
	}
	@media (hover: hover) {
		button:hover {
			color: var(--ink);
			opacity: 1;
		}
	}
	input {
		width: 4em;
		font: 13px var(--mono);
		color: var(--ink);
		background: var(--bg);
		border: 1px solid var(--rule);
		border-radius: 0;
		padding: 3px 4px;
		margin-left: 4px;
	}
	@media (max-width: 700px) {
		input {
			font-size: 16px; /* avoids iOS zoom on focus */
		}
		.hint {
			display: none;
		}
	}
</style>
