import type { Positions, RaceEvents, ResultRow } from '#lib/types.ts';
import { driverLines } from './lines.ts';
import { logoImg, type Logos } from './logos.ts';
import { axis, base, tokens } from './theme.ts';

export function positionsOption(
	positions: Positions,
	results: ResultRow[],
	logos: Logos,
	events: RaceEvents,
	all: ResultRow[] = results
) {
	const { series, tid } = driverLines(results, positions.pos, logos, events, all);
	return {
		...base(),
		grid: { top: 16, left: 36, right: 64, bottom: 32 },
		tooltip: {
			...base().tooltip,
			trigger: 'axis',
			formatter: (items: { seriesName: string; value: [number, number | null] }[]) => {
				const lap = items[0]?.value[0];
				const rows = items
					.filter((i) => i.value[1] !== null)
					.sort((a, b) => (a.value[1] as number) - (b.value[1] as number))
					.map(
						(i) =>
							`P${String(i.value[1]).padStart(2, ' ')} ${logoImg(logos, tid[i.seriesName])}${i.seriesName}`
					);
				return `${lap === 0 ? 'GRID' : `LAP ${lap}`}<br>${rows.join('<br>')}`;
			}
		},
		xAxis: { ...axis(), type: 'value', min: 0, max: positions.laps, minInterval: 1 },
		yAxis: {
			...axis(),
			type: 'value',
			inverse: true,
			min: 1,
			max: Object.keys(positions.pos).length, // all starters, even when filtered
			interval: 1,
			axisLabel: { color: tokens().muted, formatter: 'P{value}' }
		},
		series
	};
}
