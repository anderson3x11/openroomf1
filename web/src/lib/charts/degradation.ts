import { tyreColor } from '#lib/tyres.ts';
import type { Degradation, ResultRow } from '#lib/types.ts';
import { logoImg, logoRich, logoTag, type Logos } from './logos.ts';
import { axis, base, tokens } from './theme.ts';

/** One dot per stint: seconds lost per lap of tyre age, fuel corrected, tyre colored. */
export function degradationOption(stints: Degradation[], results: ResultRow[], logos: Logos) {
	const t = tokens();
	const drivers = results.map((r) => r.drv).filter((d) => stints.some((s) => s.drv === d));
	const tid = Object.fromEntries(results.map((r) => [r.drv, r.tid]));
	return {
		...base(),
		grid: { top: 8, left: 64, right: 24, bottom: 32 },
		tooltip: {
			...base().tooltip,
			trigger: 'item',
			formatter: ({ data }: { data: { s: Degradation } }) => {
				const s = data.s;
				return `${logoImg(logos, tid[s.drv])}${s.drv} STINT ${s.stint} ${s.cmp}<br>L${s.from} > L${s.to}, ${s.n} CLEAN LAPS<br>${s.deg > 0 ? '+' : ''}${s.deg.toFixed(3)} S PER LAP`;
			}
		},
		xAxis: {
			...axis(),
			type: 'value',
			axisLabel: { color: t.muted, formatter: (v: number) => `${v > 0 ? '+' : ''}${v.toFixed(2)}s` }
		},
		yAxis: {
			...axis(),
			type: 'category',
			data: drivers,
			inverse: true,
			splitLine: { show: true, lineStyle: { color: t.grid } },
			axisLabel: {
				...axis().axisLabel,
				formatter: (drv: string) => `${logoTag(logos, tid[drv])}${drv}`,
				rich: logoRich(logos)
			}
		},
		series: [
			{
				type: 'scatter',
				symbolSize: 13,
				data: stints
					.filter((s) => drivers.includes(s.drv))
					.map((s) => ({
						value: [s.deg, s.drv],
						s,
						itemStyle: { color: tyreColor(s.cmp), borderColor: t.surface, borderWidth: 2 }
					})),
				markLine: {
					silent: true,
					symbol: 'none',
					lineStyle: { color: t.muted, type: 'dashed' },
					label: { show: false },
					data: [{ xAxis: 0 }]
				}
			}
		]
	};
}
