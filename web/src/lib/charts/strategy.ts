import { tyreColor } from '#lib/tyres.ts';
import type { ResultRow, Stint } from '#lib/types.ts';
import { logoImg, logoRich, logoTag, type Logos } from './logos.ts';
import { axis, base, tokens } from './theme.ts';

/** Stints of unselected compounds are dimmed, not removed: bars are stacked from lap 0. */
export function strategyOption(
	stints: Stint[],
	results: ResultRow[],
	laps: number,
	logos: Logos,
	compounds: Set<string>
) {
	const drivers = results.map((r) => r.drv);
	const tid = Object.fromEntries(results.map((r) => [r.drv, r.tid]));
	const maxStint = Math.max(0, ...stints.map((s) => s.stint));
	const byKey = new Map(stints.map((s) => [`${s.drv}/${s.stint}`, s]));

	const series = Array.from({ length: maxStint }, (_, i) => ({
		type: 'bar',
		stack: 'laps',
		barWidth: '70%',
		data: drivers.map((drv) => {
			const s = byKey.get(`${drv}/${i + 1}`);
			if (!s) return '-';
			return {
				value: s.to - s.from + 1,
				stint: s,
				itemStyle: {
					color: tyreColor(s.cmp),
					opacity: compounds.has(s.cmp) ? 1 : 0.15,
					// The surface-colored border draws the gap between consecutive stints.
					borderColor: tokens().surface,
					borderWidth: 1
				}
			};
		})
	}));

	return {
		...base(),
		grid: { top: 8, left: 64, right: 16, bottom: 32 },
		tooltip: {
			...base().tooltip,
			trigger: 'item',
			formatter: ({ data }: { data: { stint: Stint } }) => {
				const s = data.stint;
				const tyre = s.new === false ? `USED ${s.age} LAPS` : 'NEW';
				return `${logoImg(logos, tid[s.drv])}${s.drv} STINT ${s.stint}<br>${s.cmp} ${tyre}<br>L${s.from} > L${s.to} (${s.to - s.from + 1} LAPS)`;
			}
		},
		xAxis: { ...axis(), type: 'value', min: 0, max: laps, minInterval: 1 },
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
		series
	};
}
