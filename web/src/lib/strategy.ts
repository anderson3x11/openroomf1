// Tyre strategy rows: where each stint and each pit stop falls on a shared lap axis.
import type { Driver, Stint } from './types.ts';

// Percent of the width under which two lap discs would overlap: the later one is dropped.
const MIN_GAP = 2.8;

export interface StrategyRow {
	driver: Driver;
	segments: { stint: Stint; left: number; width: number }[];
	marks: { lap: number; x: number }[]; // pit stops: the last lap of each stint but the final one
	last: number | null; // last lap of the driver
}

/** One row per driver, in the order given, on the lap range [from, to]. */
export function strategyRows(drivers: Driver[], stints: Stint[], [from, to]: [number, number]): StrategyRow[] {
	const x = (lap: number) => ((Math.min(Math.max(lap, from - 1), to) - (from - 1)) / (to - from + 1)) * 100;
	return drivers.map((driver) => {
		const own = stints.filter((s) => s.drv === driver.drv).sort((a, b) => a.from - b.from);
		const segments = own
			.filter((s) => s.to >= from && s.from <= to)
			.map((stint) => {
				const left = x(stint.from - 1);
				return { stint, left, width: x(stint.to) - left };
			});
		const marks: StrategyRow['marks'] = [];
		for (const s of own.slice(0, -1)) {
			const mark = x(s.to);
			const previous = marks.at(-1);
			if (s.to >= from && s.to <= to && (!previous || mark - previous.x >= MIN_GAP)) {
				marks.push({ lap: s.to, x: mark });
			}
		}
		return { driver, segments, marks, last: own.at(-1)?.to ?? null };
	});
}
