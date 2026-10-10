<script lang="ts">
	import Panel from '#lib/components/Panel.svelte';
	import TeamMark from '#lib/components/TeamMark.svelte';
	import { teamDuels, type DuelSide } from '#lib/duels.ts';
	import { getRace } from '#lib/race.ts';
	import { formatLap } from '#lib/stats.ts';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const race = getRace();

	const duels = $derived(
		teamDuels(data.results, data.positions, data.laptimes, data.speeds).filter(
			(d) => race.filters.drivers.has(d.a.r.drv) || race.filters.drivers.has(d.b.r.drv)
		)
	);

	type Metric = {
		label: string;
		value: (s: DuelSide) => number | null;
		show: (s: DuelSide) => string;
		better: 'low' | 'high';
	};
	const METRICS: Metric[] = [
		{ label: 'FINISH', value: (s) => s.r.pos, show: (s) => (s.r.cls.match(/^\d+$/) ? `P${s.r.cls}` : s.r.status), better: 'low' },
		{ label: 'GRID', value: (s) => s.r.grid, show: (s) => (s.r.grid ? `P${s.r.grid}` : 'PIT'), better: 'low' },
		{ label: 'LAPS AHEAD', value: (s) => s.ahead, show: (s) => String(s.ahead), better: 'high' },
		{ label: 'MEDIAN PACE', value: (s) => s.pace, show: (s) => (s.pace ? formatLap(s.pace) : ''), better: 'low' },
		{ label: 'BEST LAP', value: (s) => s.best, show: (s) => (s.best ? formatLap(s.best) : ''), better: 'low' },
		{ label: 'TOP SPEED', value: (s) => s.top, show: (s) => (s.top ? `${s.top} KM/H` : ''), better: 'high' },
		{ label: 'POINTS', value: (s) => s.r.pts, show: (s) => String(s.r.pts), better: 'high' }
	];

	/** 'a' | 'b' when one side wins the metric, '' on a tie or missing value. */
	function winner(m: Metric, a: DuelSide, b: DuelSide): 'a' | 'b' | '' {
		const [x, y] = [m.value(a), m.value(b)];
		if (x === null || y === null || x === y) return '';
		return (m.better === 'low') === x < y ? 'a' : 'b';
	}
	const score = (a: DuelSide, b: DuelSide) => {
		const w = METRICS.map((m) => winner(m, a, b));
		return [w.filter((x) => x === 'a').length, w.filter((x) => x === 'b').length];
	};
	const gap = (a: number | null, b: number | null) =>
		a !== null && b !== null ? `${(b - a).toFixed(3)}s` : '';
</script>

<div class="panels">
	{#each duels as d (d.team)}
		{@const [sa, sb] = score(d.a, d.b)}
		<Panel title={d.team} desc="Median pace on clean laps, laps ahead counted at the line. Bold: better of the two.">
			<div class="head">
				<span class="driver">
					<TeamMark src={race.logos[d.a.r.tid]} color={d.a.r.color} team={d.team} /><b>{d.a.r.drv}</b>
				</span>
				<span class="score"><b class:lead={sa > sb}>{sa}</b> - <b class:lead={sb > sa}>{sb}</b></span>
				<span class="driver right"><b>{d.b.r.drv}</b></span>
			</div>
			<table class="data">
				<tbody>
					{#each METRICS as m (m.label)}
						{@const w = winner(m, d.a, d.b)}
						<tr>
							<td class="side" class:won={w === 'a'}>{m.show(d.a)}</td>
							<td class="label metric">{m.label}</td>
							<td class="side right" class:won={w === 'b'}>{m.show(d.b)}</td>
						</tr>
					{/each}
				</tbody>
			</table>
			{#if d.a.pace && d.b.pace}
				<p class="label note">
					PACE GAP {d.b.r.drv} - {d.a.r.drv}: {gap(d.a.pace, d.b.pace)} PER LAP
				</p>
			{/if}
		</Panel>
	{/each}
</div>

<style>
	.head {
		display: grid;
		grid-template-columns: 1fr auto 1fr;
		align-items: center;
		margin-bottom: 8px;
		font: 700 22px var(--mono);
	}
	.driver {
		display: flex;
		align-items: center;
	}
	.right {
		justify-content: flex-end;
		text-align: right;
	}
	.score {
		font-size: 18px;
		color: var(--ink-muted);
	}
	.score .lead {
		color: var(--accent);
	}
	.side {
		width: 40%;
		color: var(--ink-muted);
	}
	.side.won {
		color: var(--ink);
		font-weight: 700;
	}
	.metric {
		text-align: center;
	}
	table.data td.right {
		text-align: right;
		padding-right: 0;
	}
	.note {
		margin: 10px 0 0;
	}
</style>
