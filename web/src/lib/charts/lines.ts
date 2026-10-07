// Shared pieces of the per-driver line charts (positions, gaps).
import type { RaceEvents, ResultRow } from '#lib/types.ts';
import { logoRich, logoTag, type Logos } from './logos.ts';
import { neutralMarkArea } from './neutral.ts';
import { tokens } from './theme.ts';

/** Teammates share the team color, so the lower finisher gets a dashed line. */
export function lineStyles(results: ResultRow[]): Record<string, { color: string; type: string }> {
	const seen = new Set<string>();
	const styles: Record<string, { color: string; type: string }> = {};
	for (const r of results) {
		styles[r.drv] = { color: r.color ?? tokens().muted, type: seen.has(r.team) ? 'dashed' : 'solid' };
		seen.add(r.team);
	}
	return styles;
}

/** One line per driver, cut after the last known value, labelled at its end.
 * `all`: every driver of the race, so that a driver keeps his line style when his teammate
 * is filtered out. */
export function driverLines(
	results: ResultRow[],
	values: Record<string, (number | null)[]>,
	logos: Logos,
	events: RaceEvents,
	all: ResultRow[] = results
) {
	const styles = lineStyles(all);
	const rich = logoRich(logos, 12);
	const tid = Object.fromEntries(results.map((r) => [r.drv, r.tid]));
	const series = results.map((r, i) => {
		const v = values[r.drv] ?? [];
		const last = v.findLastIndex((x) => x !== null);
		return {
			name: r.drv,
			type: 'line',
			data: v.slice(0, last + 1).map((x, lap) => [lap, x]),
			showSymbol: false,
			lineStyle: { width: 2, ...styles[r.drv] },
			itemStyle: { color: styles[r.drv].color },
			endLabel: {
				show: true,
				formatter: `${logoTag(logos, r.tid)}${r.drv}`,
				color: tokens().ink,
				fontSize: 11,
				rich
			},
			emphasis: { focus: 'series' },
			...(i === 0 ? { markArea: neutralMarkArea(events.neutral) } : {})
		};
	});
	return { series, tid };
}
