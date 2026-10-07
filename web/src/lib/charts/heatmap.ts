import { formatLap } from '#lib/stats.ts';
import type { LapMatrix, ResultRow } from '#lib/types.ts';
import { logoImg, logoRich, logoTag, type Logos } from './logos.ts';
import { axis, base, tokens } from './theme.ts';

const SPAN = 5; // seconds above the fastest clean lap mapped to the darkest color

/** Drivers x laps, colored by time lost to the fastest clean lap of the race. */
export function heatmapOption(m: LapMatrix, results: ResultRow[], logos: Logos, laps: [number, number]) {
	const t = tokens();
	const drivers = results.map((r) => r.drv);
	const tid = Object.fromEntries(results.map((r) => [r.drv, r.tid]));
	const clean = drivers.flatMap((d) =>
		(m.t[d] ?? []).filter((v, lap): v is number => v !== null && lap > 1 && m.f[d][lap] === '')
	);
	const best = Math.min(...clean);
	const cells: [number, number, number][] = [];
	const flagged: [number, number, number, string][] = [];
	drivers.forEach((d, y) => {
		(m.t[d] ?? []).forEach((v, lap) => {
			if (v === null || lap < laps[0] || lap > laps[1]) return;
			const flag = m.f[d][lap];
			if (flag) flagged.push([lap, y, v, flag]);
			else cells.push([lap, y, Math.round((v - best) * 1000) / 1000]);
		});
	});
	const flagLabel = { p: 'PIT', n: 'SC / VSC' } as Record<string, string>;

	return {
		...base(),
		grid: { top: 8, left: 64, right: 16, bottom: 56 },
		tooltip: {
			...base().tooltip,
			formatter: (p: { seriesIndex: number; value: number[]; data: (number | string)[] }) => {
				const [lap, y] = p.value;
				const d = drivers[y];
				const time = (m.t[d] ?? [])[lap] as number;
				const extra = p.seriesIndex === 1 ? flagLabel[p.data[3] as string] : `+${p.value[2].toFixed(3)}`;
				return `${logoImg(logos, tid[d])}${d} LAP ${lap}<br>${formatLap(time)} ${extra}`;
			}
		},
		xAxis: { ...axis(), type: 'category', data: Array.from({ length: m.laps + 1 }, (_, i) => i), splitLine: { show: false } },
		yAxis: {
			...axis(),
			type: 'category',
			data: drivers,
			inverse: true,
			splitLine: { show: false },
			axisLabel: {
				...axis().axisLabel,
				formatter: (drv: string) => `${logoTag(logos, tid[drv])}${drv}`,
				rich: logoRich(logos)
			}
		},
		visualMap: [
			{
			seriesIndex: 0,
			min: 0,
			max: SPAN,
			calculable: false,
			orient: 'horizontal',
			left: 'center',
			bottom: 0,
			itemWidth: 12,
			itemHeight: 160,
			text: [`+${SPAN}s SLOWER`, 'FASTEST'],
			textStyle: { color: t.muted, fontSize: 11 },
			inRange: { color: t.heat }
			},
			// ECharts wants a visual map per heatmap series: flagged laps get one flat color.
			{ type: 'piecewise', seriesIndex: 1, show: false, pieces: [{ min: 0 }], inRange: { color: [t.flagged] } }
		],
		series: [
			{ type: 'heatmap', data: cells, itemStyle: { borderColor: t.surface, borderWidth: 1 } },
			{
				type: 'heatmap',
				data: flagged,
				itemStyle: { borderColor: t.surface, borderWidth: 1 }
			}
		]
	};
}
