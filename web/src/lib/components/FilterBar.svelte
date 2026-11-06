<script lang="ts">
		import type { Filters } from '#lib/filters.ts';
	import type { Driver, RaceEvents } from '#lib/types.ts';
	import LapStrip from './LapStrip.svelte';
	import TeamMark from './TeamMark.svelte';

	let {
		filters = $bindable(),
		results,
		logos,
		compounds,
		totalLaps,
		neutral = []
	}: {
		filters: Filters;
		results: Driver[];
		logos: Record<string, string>;
		compounds: string[];
		totalLaps?: number; // no lap range filter without it (qualifying)
		neutral?: RaceEvents['neutral'];
	} = $props();
	const lastLap = $derived(totalLaps ?? filters.laps[1]);

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

	function setLap(index: 0 | 1, value: number) {
		const laps: [number, number] = [...filters.laps];
		laps[index] = Math.min(Math.max(Math.round(value) || 1, 1), lastLap);
		if (laps[0] > laps[1]) laps[1 - index] = laps[index];
		filters = { ...filters, laps };
	}

	const lastName = (name: string) => name.split(' ').slice(1).join(' ') || name;

	function reset() {
		filters = { drivers: new Set(allDrivers), laps: [1, lastLap], compounds: new Set(compounds) };
	}

	const isDefault = $derived(
		filters.drivers.size === allDrivers.length &&
			filters.laps[0] === 1 &&
			filters.laps[1] === lastLap &&
			filters.compounds.size === compounds.length
	);
</script>

<div class="filters">
	<div class="summary">
		<button class="label toggle" aria-expanded={open} onclick={() => (open = !open)}>
			FILTERS {open ? '-' : '+'}
		</button>
		<span class="label state">
			<b>{filters.drivers.size}/{allDrivers.length}</b> DRIVERS
			{#if totalLaps}<span aria-hidden="true">/</span> LAPS <b>{filters.laps[0]}-{filters.laps[1]}</b>{/if}
		</span>
		{#if !isDefault}
			<button class="label link reset" onclick={reset}>RESET</button>
		{/if}
	</div>

	<div class="body" class:open>
		<div class="row">
			<span class="label title">Drivers</span>
			<button class="label link" onclick={() => setDrivers(allDrivers)}>ALL</button>
			<button class="label link" onclick={() => setDrivers([])}>NONE</button>
		</div>
		<div class="teams">
			{#each teams as t (t.team)}
				{@const drvs = t.drivers.map((d) => d.drv)}
				<div class="team" style:--team={t.color}>
					<button
						class="logo"
						title="{t.team}: click to show or hide, double click to isolate"
						aria-label="Team {t.team}"
						aria-pressed={drvs.every((d) => filters.drivers.has(d))}
						onclick={() => toggle(drvs)}
						ondblclick={() => setDrivers(drvs)}
					>
						<TeamMark src={logos[t.tid]} color={t.color} team={t.team} />
					</button>
					<div class="drivers">
						{#each t.drivers as d (d.drv)}
							<button
								class="driver"
								aria-pressed={filters.drivers.has(d.drv)}
								title="{d.name}: click to show or hide, double click to isolate"
								onclick={() => toggle([d.drv])}
								ondblclick={() => setDrivers([d.drv])}
							>
								<span class="dot"></span><b>{d.drv}</b><span class="name">{lastName(d.name)}</span>
							</button>
						{/each}
					</div>
				</div>
			{/each}
		</div>
		{#if totalLaps}
			<div class="row laps">
				<span class="label title">Laps</span>
				{#if filters.laps[0] !== 1 || filters.laps[1] !== totalLaps}
					<button class="label link" onclick={() => (filters = { ...filters, laps: [1, totalLaps] })}>ALL</button>
				{/if}
				<input
					type="number"
					aria-label="First lap"
					min="1"
					max={totalLaps}
					value={filters.laps[0]}
					onchange={(e) => setLap(0, e.currentTarget.valueAsNumber)}
				/>
				<span class="label">to</span>
				<input
					type="number"
					aria-label="Last lap"
					min="1"
					max={totalLaps}
					value={filters.laps[1]}
					onchange={(e) => setLap(1, e.currentTarget.valueAsNumber)}
				/>
			</div>
			<LapStrip bind:laps={() => filters.laps, (laps) => (filters = { ...filters, laps })} total={totalLaps} {neutral} />
		{/if}
	</div>
</div>

<style>
	.filters {
		display: flex;
		flex-direction: column;
		background: var(--panel);
		border-radius: var(--radius);
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
		display: none;
		gap: 10px;
		padding: 14px;
		border-top: 1px solid var(--rule-soft);
	}
	.body.open {
		display: grid;
	}
	.row {
		display: flex;
		align-items: center;
		gap: 10px;
	}
	.laps {
		margin-top: 8px;
		gap: 6px;
	}
	.title {
		font: 700 13px/1.2 var(--sans);
		letter-spacing: 0;
		text-transform: none;
		color: var(--ink);
		margin-right: auto;
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
	.teams {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
	}
	.team {
		display: grid;
		grid-template-columns: 30px minmax(0, 1fr);
		gap: 4px;
		padding: 4px 0;
		border-top: 1px solid var(--rule-soft);
	}
	.logo {
		display: grid;
		place-items: center;
		padding: 0;
		border-radius: 8px;
		opacity: 0.45;
	}
	.logo[aria-pressed='true'] {
		opacity: 1;
	}
	.logo :global(img) {
		margin: 0;
	}
	.driver {
		display: grid;
		grid-template-columns: 8px 2.7rem minmax(0, 1fr);
		align-items: center;
		gap: 8px;
		width: 100%;
		height: 28px;
		padding: 0 8px;
		text-align: left;
		letter-spacing: 0;
		border-radius: 8px;
	}
	.dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		box-shadow: inset 0 0 0 1.5px var(--rule);
	}
	.driver b {
		font: 700 12px/1 var(--sans);
	}
	.name {
		overflow: hidden;
		white-space: nowrap;
		text-overflow: ellipsis;
		font-size: 12px;
	}
	.driver[aria-pressed='false'] :is(b, .name) {
		opacity: 0.45;
	}
	.driver[aria-pressed='true'] .dot {
		background: var(--team, var(--ink));
		box-shadow: none;
	}
	.driver[aria-pressed='true'] b {
		color: var(--ink);
	}
	@media (hover: hover) {
		.link:hover {
			color: var(--ink);
		}
		.logo:hover,
		.driver:hover {
			background: var(--rule-soft);
		}
	}
	input {
		width: 2.8em;
		font: 600 13px var(--mono);
		text-align: center;
		color: var(--ink);
		background: var(--bg);
		border: 0;
		border-radius: 8px;
		padding: 5px 0;
		appearance: textfield;
	}
	input::-webkit-inner-spin-button {
		appearance: none;
	}
	/* Wide screens: always open, the whole height of the list. */
	@media (min-width: 1100px) {
		.filters {
			max-height: calc(100dvh - 24px);
			overflow-y: auto;
			scrollbar-width: thin;
		}
		.summary {
			order: 1;
			padding: 0;
		}
		.toggle,
		.state {
			display: none;
		}
		.reset {
			padding: 0 18px 18px;
		}
		.body {
			display: grid;
			padding: 18px;
			border-top: 0;
		}
		.teams {
			grid-template-columns: minmax(0, 1fr);
		}
		/* All 22 drivers and the laps fit in the window, roomier when it is tall. */
		.driver {
			height: clamp(22px, calc((100dvh - 310px) / 22), 30px);
		}
	}
	@media (max-width: 700px) {
		input {
			font-size: 16px; /* avoids iOS zoom on focus */
		}
	}
</style>
