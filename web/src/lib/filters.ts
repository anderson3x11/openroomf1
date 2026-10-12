// Global page filters. Pure helpers, applied to the race data before building charts and tables.
import type { Driver, LapTimes, PitStop, RaceEvents, Stint } from '#lib/types.ts';

export interface Filters {
	drivers: Set<string>;
	laps: [number, number];
	compounds: Set<string>;
}

export const inLaps = (lap: number, [from, to]: [number, number]) => lap >= from && lap <= to;

export function filterResults<T extends Driver>(results: T[], f: Filters) {
	return results.filter((r) => f.drivers.has(r.drv));
}

export function filterStints(stints: Stint[], f: Filters) {
	return stints.filter((s) => f.drivers.has(s.drv));
}

export function filterPitStops(stops: PitStop[], f: Filters) {
	return stops.filter((s) => f.drivers.has(s.drv) && inLaps(s.lap, f.laps));
}

/** Keeps a lap only if its driver, lap number and tyre compound are selected. */
export function filterLapTimes(laptimes: LapTimes, stints: Stint[], f: Filters): LapTimes {
	const compoundOf = (drv: string, lap: number) =>
		stints.find((s) => s.drv === drv && lap >= s.from && lap <= s.to)?.cmp ?? 'UNKNOWN';
	return Object.fromEntries(
		Object.entries(laptimes)
			.filter(([drv]) => f.drivers.has(drv))
			.map(([drv, laps]) => [
				drv,
				laps.filter(([lap]) => inLaps(lap, f.laps) && f.compounds.has(compoundOf(drv, lap)))
			])
	);
}

/** Messages in the lap range, about a selected driver or about nobody in particular. */
export function filterEvents(events: RaceEvents, f: Filters): RaceEvents {
	return {
		neutral: events.neutral,
		msgs: events.msgs.filter(
			(m) => inLaps(m.lap, f.laps) && (m.drv.length === 0 || m.drv.some((d) => f.drivers.has(d)))
		)
	};
}

/** Zoom a lap-based x axis on the selected range. */
export function withLapRange<T extends { xAxis: object }>(option: T, [from, to]: [number, number]): T {
	return { ...option, xAxis: { ...option.xAxis, min: from - 1, max: to } };
}

/** Filters as URL query values, to share a view: only what differs from `all` is written.
 * d: drivers, l: lap range, c: compounds. */
export function filtersToParams(f: Filters, all: Filters): Record<string, string | null> {
	const same = (a: Set<string>, b: Set<string>) => a.size === b.size && [...a].every((x) => b.has(x));
	return {
		d: same(f.drivers, all.drivers) ? null : [...f.drivers].join(','),
		l: f.laps[0] === all.laps[0] && f.laps[1] === all.laps[1] ? null : `${f.laps[0]}-${f.laps[1]}`,
		c: same(f.compounds, all.compounds) ? null : [...f.compounds].join(',')
	};
}

/** Inverse of filtersToParams; unknown drivers, compounds and laps out of range are dropped. */
export function filtersFromParams(params: URLSearchParams, all: Filters): Filters {
	const pick = (key: string, valid: Set<string>) => {
		const v = params.get(key);
		return v === null ? new Set(valid) : new Set(v.split(',').filter((x) => valid.has(x)));
	};
	const [from, to] = (params.get('l') ?? '').split('-').map(Number);
	const inRange = (n: number) => Number.isInteger(n) && n >= all.laps[0] && n <= all.laps[1];
	return {
		drivers: pick('d', all.drivers),
		laps: inRange(from) && inRange(to) && from <= to ? [from, to] : [...all.laps],
		compounds: pick('c', all.compounds)
	};
}
