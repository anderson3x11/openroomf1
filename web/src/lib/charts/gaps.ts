import type { Gaps, RaceEvents, ResultRow } from '#lib/types.ts';
import { driverLines } from './lines.ts';
import { logoImg, type Logos } from './logos.ts';
import { axis, base, tokens } from './theme.ts';

/** Gaps to a reference driver instead of the leader: negative = ahead of him. */
export function relativeGaps(gaps: Gaps, ref: string): Gaps['gap'] {
	const base = gaps.gap[ref] ?? [];
	return Object.fromEntries(
		Object.entries(gaps.gap).map(([drv, g]) => [
			drv,
			g.map((v, lap) => (v === null || base[lap] == null ? null : Math.round((v - base[lap]) * 1000) / 1000))
		])
	);
}

/** ref: driver code to measure gaps from, or '' for the leader of each lap. */
export function gapsOption(
	gaps: Gaps,
	results: ResultRow[],
	logos: Logos,
	events: RaceEvents,
	ref = '',
	all: ResultRow[] = results
) {
	const t = tokens();
	const values = ref ? relativeGaps(gaps, ref) : gaps.gap;
	const { series, tid } = driverLines(results, values, logos, events, all);
	const fmt = (v: number) => `${v > 0 ? '+' : ''}${v.toFixed(3)}`;
	return {
		...base(),
		grid: { top: 16, left: 48, right: 88, bottom: 32 },
		// Lapped cars and safety car laps crush the scale: open on the first minute, slider to widen.
		dataZoom: [
			{
				type: 'slider',
				yAxisIndex: 0,
				right: 8,
				width: 14,
				startValue: ref ? -30 : 0,
				endValue: ref ? 30 : 60,
				filterMode: 'none',
				borderColor: t.rule,
				backgroundColor: t.tooltip,
				fillerColor: translucent(t.ink),
				handleStyle: { color: t.ink, borderColor: t.ink },
				dataBackground: { lineStyle: { opacity: 0 }, areaStyle: { opacity: 0 } },
				labelFormatter: (v: number) => `${v > 0 ? '+' : ''}${Math.round(v)}s`,
				textStyle: { color: t.muted, fontSize: 11 }
			},
			{ type: 'inside', yAxisIndex: 0, filterMode: 'none' }
		],
		tooltip: {
			...base().tooltip,
			trigger: 'axis',
			formatter: (items: { seriesName: string; value: [number, number | null] }[]) => {
				const rows = items
					.filter((i) => i.value[1] !== null)
					.sort((a, b) => (a.value[1] as number) - (b.value[1] as number))
					.map(
						(i) =>
							`${logoImg(logos, tid[i.seriesName])}${i.seriesName} ${fmt(i.value[1] as number)}`
					);
				return `LAP ${items[0]?.value[0]}<br>${rows.join('<br>')}`;
			}
		},
		xAxis: { ...axis(), type: 'value', min: 0, max: gaps.laps, minInterval: 1 },
		yAxis: {
			...axis(),
			type: 'value',
			inverse: true,
			min: ref ? undefined : 0,
			// Zoom bounds are not round numbers: labels are rounded to the second.
			axisLabel: { color: t.muted, formatter: (v: number) => `${v > 0 ? '+' : ''}${Math.round(v)}s` }
		},
		series
	};
}

/** #RRGGBB -> translucent fill for the zoom window. */
function translucent(hex: string) {
	return `${hex}26`;
}
