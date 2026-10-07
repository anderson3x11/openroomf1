// Teammate duels, from data the GP pages already load.
import { quantile } from './stats.ts';
import type { LapTimes, Positions, ResultRow, Speeds } from './types.ts';

export interface DuelSide {
	r: ResultRow;
	ahead: number; // laps completed ahead of the teammate on track
	pace: number | null; // median clean lap, s
	best: number | null;
	top: number | null;
}

export interface Duel {
	team: string;
	a: DuelSide;
	b: DuelSide;
}

/** One duel per team, the two drivers in finishing order (a team with a mid-season third
 * driver keeps its two best finishers). */
export function teamDuels(
	results: ResultRow[],
	positions: Positions,
	laptimes: LapTimes,
	speeds: Record<string, Speeds>
): Duel[] {
	const teams = [...new Set(results.map((r) => r.team))];
	return teams.flatMap((team) => {
		const [ra, rb] = results.filter((r) => r.team === team);
		if (!ra || !rb) return [];
		const pa = positions.pos[ra.drv] ?? [];
		const pb = positions.pos[rb.drv] ?? [];
		let aheadA = 0;
		let aheadB = 0;
		for (let lap = 1; lap < Math.max(pa.length, pb.length); lap++) {
			const [x, y] = [pa[lap], pb[lap]];
			if (x == null || y == null) continue;
			if (x < y) aheadA++;
			else aheadB++;
		}
		const side = (r: ResultRow, ahead: number): DuelSide => {
			const laps = (laptimes[r.drv] ?? []).map(([, t]) => t).sort((p, q) => p - q);
			return {
				r,
				ahead,
				pace: laps.length ? quantile(laps, 0.5) : null,
				best: speeds[r.drv]?.best ?? null,
				top: speeds[r.drv]?.top ?? null
			};
		};
		return [{ team, a: side(ra, aheadA), b: side(rb, aheadB) }];
	});
}
