import { delta } from '#lib/telemetry.ts';
import type { Telemetry } from '#lib/types.ts';
import { axis, base, tokens } from './theme.ts';

const ALL_PANELS = [
	{ key: 'v', label: 'SPEED KM/H', h: 220 },
	{ key: 'delta', label: 'DELTA S', h: 110 },
	{ key: 'thr', label: 'THROTTLE %', h: 80 },
	{ key: 'brk', label: 'BRAKE', h: 36 },
	{ key: 'g', label: 'GEAR', h: 80 },
	{ key: 'rpm', label: 'RPM', h: 80 },
	{ key: 'drs', label: 'DRS', h: 36 }
] as const;
const GAP = 22;
const TOP = 16;
const BOTTOM = 56; // distance labels and zoom slider

/** No DRS panel when none of the laps opened it (2026 cars have no DRS). */
const panels = (tel: Telemetry, drivers: string[]) =>
	ALL_PANELS.filter((p) => p.key !== 'drs' || drivers.some((d) => tel.laps[d]?.drs.includes(1)));

export const telemetryHeight = (tel: Telemetry, drivers: string[]) =>
	TOP + panels(tel, drivers).reduce((h, p) => h + p.h + GAP, 0) + BOTTOM;

/** Best laps of the chosen drivers, channel by channel on one distance axis. The delta is to
 * the first driver of `drivers`. */
export function telemetryOption(tel: Telemetry, drivers: string[], colors: Record<string, string>) {
	const t = tokens();
	const shown = panels(tel, drivers);
	const laps = drivers.map((d) => tel.laps[d]).filter(Boolean);
	const ref = laps[0];
	let top = TOP;
	const grids = shown.map((p) => {
		const g = { top, height: p.h, left: 64, right: 24 };
		top += p.h + GAP;
		return g;
	});
	const all = shown.map((_, i) => i);
	const last = shown.length - 1;

	const series = shown.flatMap((p, i) =>
		drivers
			.filter((d) => tel.laps[d])
			.map((d) => {
				const lap = tel.laps[d];
				const values = p.key === 'delta' ? delta(ref, lap) : lap[p.key];
				return {
					type: 'line',
					name: d,
					xAxisIndex: i,
					yAxisIndex: i,
					showSymbol: false,
					step: p.key === 'brk' || p.key === 'drs' || p.key === 'g' ? 'end' : undefined,
					lineStyle: { width: p.key === 'v' ? 1.8 : 1.4, color: colors[d] },
					itemStyle: { color: colors[d] },
					data: values.map((v, j) => [j * tel.step, v])
				};
			})
	);

	return {
		...base(),
		grid: grids,
		axisPointer: { link: [{ xAxisIndex: 'all' }], lineStyle: { color: t.muted } },
		tooltip: {
			...base().tooltip,
			trigger: 'axis',
			axisPointer: { type: 'line' },
			valueFormatter: (v: number) => String(v)
		},
		dataZoom: [
			{ type: 'inside', xAxisIndex: all },
			{
				type: 'slider',
				xAxisIndex: all,
				bottom: 8,
				height: 18,
				borderColor: t.rule,
				textStyle: { color: t.muted },
				labelFormatter: (v: number) => `${Math.round(v)} M`
			}
		],
		xAxis: shown.map((_, i) => ({
			...axis(),
			type: 'value',
			gridIndex: i,
			min: 0,
			max: (v: { max: number }) => v.max,
			splitLine: { show: false },
			axisLabel: { show: i === last, color: t.muted, formatter: (v: number) => `${v} M` }
		})),
		yAxis: shown.map((p, i) => ({
			...axis(),
			type: 'value',
			gridIndex: i,
			scale: p.key === 'v' || p.key === 'rpm' || p.key === 'delta',
			min: p.key === 'brk' || p.key === 'drs' ? 0 : undefined,
			max: p.key === 'brk' || p.key === 'drs' ? 1 : p.key === 'thr' ? 100 : undefined,
			splitNumber: p.h < 60 ? 1 : 3,
			name: p.label,
			nameLocation: 'end',
			nameGap: 6,
			nameTextStyle: { color: t.muted, fontSize: 11, align: 'left', padding: [0, 0, 0, -56] },
			axisLabel: { color: t.muted, fontSize: 11, show: p.h >= 60 }
		})),
		series
	};
}
