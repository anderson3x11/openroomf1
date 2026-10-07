import type { RaceEvents, RaceTrace, ResultRow } from '#lib/types.ts';
import { driverLines } from './lines.ts';
import { logoImg, type Logos } from './logos.ts';
import { axis, base, tokens } from './theme.ts';

/** Classic race trace: above zero = ahead of the winner's average pace, pit stops show as drops. */
export function raceTraceOption(
	trace: RaceTrace,
	results: ResultRow[],
	logos: Logos,
	events: RaceEvents,
	all: ResultRow[] = results
) {
	const t = tokens();
	const { series, tid } = driverLines(results, trace.trace, logos, events, all);
	const fmt = (v: number) => `${v > 0 ? '+' : ''}${v.toFixed(1)}s`;
	// A car parked in the garage or a red flag can sit 1000 s down and crush the scale:
	// open between the 5th percentile and the top, slider or wheel to see the rest.
	const values = results
		.flatMap((r) => trace.trace[r.drv] ?? [])
		.filter((v): v is number => v !== null)
		.sort((a, b) => a - b);
	const low = values.length ? values[Math.floor(values.length * 0.05)] : 0;
	const high = values.length ? values[values.length - 1] : 0;
	return {
		...base(),
		grid: { top: 16, left: 56, right: 104, bottom: 32 },
		dataZoom: [
			{
				type: 'slider',
				yAxisIndex: 0,
				right: 8,
				width: 14,
				startValue: Math.floor(low / 10) * 10,
				endValue: Math.ceil(high / 10) * 10,
				filterMode: 'none',
				borderColor: t.rule,
				backgroundColor: t.tooltip,
				fillerColor: `${t.ink}26`,
				handleStyle: { color: t.ink, borderColor: t.ink },
				dataBackground: { lineStyle: { opacity: 0 }, areaStyle: { opacity: 0 } },
				labelFormatter: (v: number) => `${Math.round(v)}s`,
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
					.sort((a, b) => (b.value[1] as number) - (a.value[1] as number))
					.map((i) => `${logoImg(logos, tid[i.seriesName])}${i.seriesName} ${fmt(i.value[1] as number)}`);
				return `LAP ${items[0]?.value[0]}<br>${rows.join('<br>')}`;
			}
		},
		xAxis: { ...axis(), type: 'value', min: 0, max: trace.laps, minInterval: 1 },
		yAxis: {
			...axis(),
			type: 'value',
			axisLabel: { color: t.muted, formatter: (v: number) => `${v > 0 ? '+' : ''}${Math.round(v)}s` }
		},
		series
	};
}
