import { boxStats, formatLap } from '#lib/stats.ts';
import type { LapTimes, ResultRow } from '#lib/types.ts';
import { logoImg, logoRich, logoTag, type Logos } from './logos.ts';
import { axis, base, tokens } from './theme.ts';

/** Box plot per driver, fastest median first. Clean laps only (see LapTimes). */
export function laptimesOption(laptimes: LapTimes, results: ResultRow[], logos: Logos) {
	const byDrv = new Map(results.map((r) => [r.drv, r]));
	const rows = Object.entries(laptimes)
		.filter(([, laps]) => laps.length >= 5)
		.map(([drv, laps]) => ({ drv, ...boxStats(laps.map(([, t]) => t)) }))
		.sort((a, b) => a.box[2] - b.box[2]);
	const drivers = rows.map((r) => r.drv);
	const color = (drv: string) => byDrv.get(drv)?.color ?? tokens().muted;
	const tid = (drv: string) => byDrv.get(drv)?.tid ?? '';

	return {
		...base(),
		grid: { top: 8, left: 64, right: 16, bottom: 32 },
		tooltip: {
			...base().tooltip,
			trigger: 'item',
			formatter: (p: { seriesType: string; name: string; value: number[]; data: { n: number } }) => {
				if (p.seriesType !== 'boxplot') return `${p.name} ${formatLap(p.value[0])}`;
				const [, min, q1, med, q3, max] = p.value;
				return [
					`${logoImg(logos, tid(p.name))}${p.name} (${p.data.n} LAPS)`,
					`MEDIAN ${formatLap(med)}`,
					`Q1-Q3 ${formatLap(q1)} / ${formatLap(q3)}`,
					`MIN-MAX ${formatLap(min)} / ${formatLap(max)}`
				].join('<br>');
			}
		},
		xAxis: {
			...axis(),
			type: 'value',
			scale: true,
			axisLabel: { color: tokens().muted, formatter: (v: number) => formatLap(v) }
		},
		yAxis: {
			...axis(),
			type: 'category',
			data: drivers,
			inverse: true,
			splitLine: { show: false },
			axisLabel: {
				...axis().axisLabel,
				formatter: (drv: string) => `${logoTag(logos, tid(drv))}${drv}`,
				rich: logoRich(logos)
			}
		},
		series: [
			{
				type: 'boxplot',
				layout: 'horizontal',
				boxWidth: [6, 14],
				data: rows.map((r) => ({
					name: r.drv,
					value: r.box,
					n: laptimes[r.drv].length,
					itemStyle: { color: `${color(r.drv)}33`, borderColor: color(r.drv), borderWidth: 1.5 }
				}))
			},
			{
				type: 'scatter',
				symbolSize: 5,
				data: rows.flatMap((r) =>
					r.outliers.map((t) => ({ name: r.drv, value: [t, r.drv], itemStyle: { color: color(r.drv) } }))
				)
			}
		]
	};
}
