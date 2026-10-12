// Lap comparison helpers: delta between two laps, fastest driver per mini-sector, colors.
import type { Driver, TelemetryLap } from './types.ts';

/** Time lost (+) or gained (-) to the reference lap at every point, seconds. */
export const delta = (ref: TelemetryLap, lap: TelemetryLap) =>
	lap.t.map((t, i) => Math.round(t - ref.t[i]) / 1000);

/** Split the lap in n mini-sectors of equal distance; for each, the index of the fastest lap
 * through it. Mini-sector k covers points [from, to]. */
export function miniSectors(laps: TelemetryLap[], n: number) {
	const points = Math.min(...laps.map((l) => l.t.length));
	return Array.from({ length: n }, (_, k) => {
		const from = Math.floor((k * (points - 1)) / n);
		const to = Math.floor(((k + 1) * (points - 1)) / n);
		const times = laps.map((l) => l.t[to] - l.t[from]);
		return { from, to, best: times.indexOf(Math.min(...times)) };
	});
}

// For a second driver of the same team: teammates share a team color.
const SPARE = ['#FFFFFF', '#B07CFF', '#00C2FF', '#FF8A00'];

/** One distinct color per driver: the team color, or a spare one for a teammate. */
export function distinctColors(drivers: Driver[]): Record<string, string> {
	const used = new Set<string>();
	const out: Record<string, string> = {};
	for (const d of drivers) {
		const color = d.color && !used.has(d.color) ? d.color : (SPARE.find((c) => !used.has(c)) ?? '#888888');
		used.add(color);
		out[d.drv] = color;
	}
	return out;
}
