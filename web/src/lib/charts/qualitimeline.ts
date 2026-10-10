import { formatLap } from '#lib/stats.ts';
import type { Driver, QualiLaps } from '#lib/types.ts';
import { logoImg, type Logos } from './logos.ts';
import { axis, base, tokens } from './theme.ts';

/** Every flying lap against session time: track evolution and each driver's runs, segment by
 * segment. Teammates share the team color, so the second one gets a diamond. Hollow: deleted. */
export function qualiTimelineOption(data: QualiLaps, drivers: Driver[], logos: Logos, compounds: Set<string>) {
	const t = tokens();
	const t0 = Math.min(...data.segs.map(([, start]) => start));
	const minute = (s: number) => (s - t0) / 60;
	const seen = new Set<string>();

	const series = drivers.map((d) => {
		const symbol = seen.has(d.team) ? 'diamond' : 'circle';
		seen.add(d.team);
		const color = d.color ?? t.muted;
		return {
			type: 'scatter',
			name: d.drv,
			symbol,
			symbolSize: 8,
			data: (data.laps[d.drv] ?? [])
				.filter(([, , , cmp]) => compounds.has(cmp))
				.map(([seg, at, lap, cmp, deleted]) => ({
					value: [minute(at), lap],
					seg,
					cmp,
					deleted,
					itemStyle: deleted
						? { color: 'transparent', borderColor: color, borderWidth: 1.5 }
						: { color }
				})),
			tid: d.tid
		};
	});

	return {
		...base(),
		grid: { top: 28, left: 72, right: 16, bottom: 36 },
		tooltip: {
			...base().tooltip,
			trigger: 'item',
			formatter: (p: {
				seriesName: string;
				seriesIndex: number;
				data: { value: [number, number]; seg: number; cmp: string; deleted: number };
			}) =>
				`${logoImg(logos, series[p.seriesIndex]?.tid ?? '')}${p.seriesName} ${formatLap(p.data.value[1])}<br>` +
				`Q${p.data.seg} / ${p.data.cmp}${p.data.deleted ? ' / DELETED' : ''}`
		},
		xAxis: {
			...axis(),
			type: 'value',
			name: 'MIN',
			nameTextStyle: { color: t.muted },
			min: 0,
			max: (v: { max: number }) => Math.ceil(v.max),
			splitLine: { show: false }
		},
		yAxis: {
			...axis(),
			type: 'value',
			scale: true,
			axisLabel: { color: t.muted, formatter: (v: number) => formatLap(v) }
		},
		series: [
			...series,
			{
				// Segment bands, on a series of their own so they stay when drivers are hidden.
				type: 'scatter',
				data: [],
				silent: true,
				markArea: {
					silent: true,
					label: { color: t.muted, fontSize: 11, position: 'insideTop' },
					data: data.segs.map(([seg, start, end]) => [
						{ xAxis: minute(start), name: `Q${seg}`, itemStyle: { color: seg % 2 ? t.neutral : 'transparent' } },
						{ xAxis: minute(end) }
					])
				}
			}
		]
	};
}
