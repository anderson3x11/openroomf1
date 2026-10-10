// Qualifying classification helpers: segment reached, gap, knockout lines.
import type { QualiRow } from './types.ts';

/** Fastest time of each segment (Q1, Q2, Q3) among the rows, null when nobody set one. */
export function fastestBySegment(rows: QualiRow[]): (number | null)[] {
	return [0, 1, 2].map((i) => {
		const times = rows.map((r) => r.q[i]).filter((t): t is number => t !== null);
		return times.length ? Math.min(...times) : null;
	});
}

/** Per row: last segment with a time (0-2, -1 = none), gap to the fastest of that segment, and
 * whether a knockout line goes above it (first row out of a later segment). */
export function qualiLines(rows: QualiRow[]) {
	const fastest = fastestBySegment(rows);
	return rows.map((r, i) => {
		const reached = r.q.findLastIndex((t) => t !== null);
		const best = fastest[reached];
		const prev = i > 0 ? rows[i - 1].q.findLastIndex((t) => t !== null) : reached;
		return {
			row: r,
			reached,
			gap: reached >= 0 && best !== null ? (r.q[reached] as number) - best : null,
			cut: reached < prev
		};
	});
}
