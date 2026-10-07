import type { Positions, ResultRow } from '#lib/types.ts';
import { logoImg, logoRich, logoTag, type Logos } from './logos.ts';
import { axis, base, tokens } from './theme.ts';

/** Places gained or lost on lap 1: grid slot minus position at the end of lap 1. */
export function lapOneGains(positions: Positions, results: ResultRow[]) {
	return results
		.map((r) => {
			const [grid, lap1] = positions.pos[r.drv] ?? [];
			return grid != null && lap1 != null ? { drv: r.drv, grid, lap1, gain: grid - lap1 } : null;
		})
		.filter((g) => g !== null)
		.sort((a, b) => b.gain - a.gain || a.lap1 - b.lap1);
}

export function startOption(positions: Positions, results: ResultRow[], logos: Logos) {
	const t = tokens();
	const rows = lapOneGains(positions, results);
	const tid = Object.fromEntries(results.map((r) => [r.drv, r.tid]));
	return {
		...base(),
		grid: { top: 8, left: 64, right: 40, bottom: 28 },
		tooltip: {
			...base().tooltip,
			trigger: 'item',
			formatter: ({ dataIndex }: { dataIndex: number }) => {
				const r = rows[dataIndex];
				return `${logoImg(logos, tid[r.drv])}${r.drv}<br>GRID P${r.grid} > LAP 1 P${r.lap1}`;
			}
		},
		xAxis: { ...axis(), type: 'value', minInterval: 1, axisLabel: { color: t.muted, formatter: (v: number) => (v > 0 ? `+${v}` : `${v}`) } },
		yAxis: {
			...axis(),
			type: 'category',
			data: rows.map((r) => r.drv),
			inverse: true,
			splitLine: { show: false },
			axisLabel: {
				...axis().axisLabel,
				formatter: (drv: string) => `${logoTag(logos, tid[drv])}${drv}`,
				rich: logoRich(logos)
			}
		},
		series: [
			{
				type: 'bar',
				barWidth: '60%',
				data: rows.map((r) => ({
					value: r.gain,
					itemStyle: { color: r.gain > 0 ? t.gain : r.gain < 0 ? t.loss : t.muted }
				})),
				label: {
					show: true,
					position: 'right',
					color: t.ink,
					fontSize: 11,
					formatter: ({ value }: { value: number }) => (value > 0 ? `+${value}` : value === 0 ? '0' : `${value}`)
				}
			}
		]
	};
}
