// Global page filters. Pure helpers, applied to the race data before building charts and tables.
import type { LapTimes, PitStop, RaceEvents, ResultRow, Stint } from '#lib/types.ts';

export interface Filters {
	drivers: Set<string>;
	laps: [number, number];
	compounds: Set<string>;
}

export const inLaps = (lap: number, [from, to]: [number, number]) => lap >= from && lap <= to;

export function filterResults(results: ResultRow[], f: Filters) {
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
