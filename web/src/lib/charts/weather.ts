import type { Weather } from '#lib/types.ts';
import { axis, base, tokens } from './theme.ts';

const RAIN = 'rgba(80, 150, 255, 0.16)';

/** Lap ranges where it rained, as shaded bands. */
function rainBands(w: Weather) {
	const bands: [{ xAxis: number }, { xAxis: number }][] = [];
	let start: number | null = null;
	w.rain.forEach((wet, i) => {
		if (wet && start === null) start = w.lap[i];
		if (!wet && start !== null) {
			bands.push([{ xAxis: start }, { xAxis: w.lap[i] }]);
			start = null;
		}
	});
	if (start !== null) bands.push([{ xAxis: start }, { xAxis: w.lap[w.lap.length - 1] }]);
	return bands;
}

/** Track and air temperature on the race lap axis, rain as blue bands. */
export function weatherOption(w: Weather, laps: number) {
	const t = tokens();
	const line = (name: string, values: number[], color: string, width: number) => ({
		name,
		type: 'line',
		data: w.lap.map((lap, i) => [lap, values[i]]),
		showSymbol: false,
		lineStyle: { width, color },
		itemStyle: { color },
		endLabel: { show: true, formatter: name, color: t.ink, fontSize: 11 }
	});
	return {
		...base(),
		grid: { top: 16, left: 48, right: 72, bottom: 32 },
		tooltip: {
			...base().tooltip,
			trigger: 'axis',
			formatter: (items: { dataIndex: number }[]) => {
				const i = items[0]?.dataIndex ?? 0;
				return [
					`LAP ${Math.floor(w.lap[i]) + 1}`,
					`TRACK ${w.track[i]}°C / AIR ${w.air[i]}°C`,
					`HUMIDITY ${w.humidity[i]}% / WIND ${w.wind[i]} m/s`,
					w.rain[i] ? 'RAIN' : 'DRY'
				].join('<br>');
			}
		},
		xAxis: { ...axis(), type: 'value', min: 0, max: laps, minInterval: 1 },
		yAxis: { ...axis(), type: 'value', scale: true, axisLabel: { color: t.muted, formatter: '{value}°C' } },
		series: [
			{ ...line('TRACK', w.track, t.ink, 2), markArea: { silent: true, itemStyle: { color: RAIN }, data: rainBands(w) } },
			line('AIR', w.air, t.muted, 2)
		]
	};
}
