import { tyreColor } from '#lib/tyres.ts';
import type { ResultRow, Stint } from '#lib/types.ts';
import { logoImg, logoRich, logoTag, type Logos } from './logos.ts';
import { axis, base, tokens } from './theme.ts';

// Hatching of used tyres, drawn over the compound color (ECharts decal pattern).
const USED = {
	symbol: 'rect',
	dashArrayX: [1, 0],
	dashArrayY: [2, 4],
	rotation: -Math.PI / 4,
	color: 'rgba(0, 0, 0, 0.55)'
};

/** Stints of unselected compounds are dimmed, not removed: bars are stacked from lap 0.
 * Like the Pirelli graphics: used tyres hatched, the last lap of each stint written at its end
 * (pit stop lap, then the final lap). */
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
		barWidth: '50%',
		label: {
			show: true,
			position: 'insideRight',
			fontSize: 10,
			fontWeight: 700,
			formatter: ({ data }: { data: { stint: Stint } }) => String(data.stint.to)
		},
		labelLayout: { hideOverlap: true },
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
					borderWidth: 1,
					decal: s.new === false ? USED : { symbol: 'none' }
				},
				label: { color: s.cmp === 'MEDIUM' || s.cmp === 'HARD' ? '#111111' : '#FFFFFF' }
			};
		})
	}));

	return {
		...base(),
		aria: { enabled: true, decal: { show: true } }, // needed for the hatching
		grid: { top: 8, left: 64, right: 16, bottom: 32 },
		tooltip: {
			...base().tooltip,
			trigger: 'item',
			formatter: ({ data }: { data: { stint: Stint } }) => {
				const s = data.stint;
				const tyre = s.new === null ? 'AGE UNKNOWN' : s.new ? 'NEW' : `USED ${s.age} LAPS`;
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
