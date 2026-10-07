import { raceData } from '#lib/server/data.ts';
import type { Gaps, LapMatrix, LapTimes, RaceTrace, Speeds } from '#lib/types.ts';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
	const [gaps, laptimes, lapMatrix, raceTrace, speeds] = await Promise.all([
		raceData<Gaps>(params, 'gaps'),
		raceData<LapTimes>(params, 'laptimes'),
		raceData<LapMatrix>(params, 'laps'),
		raceData<RaceTrace>(params, 'racetrace'),
		raceData<Record<string, Speeds>>(params, 'speeds').catch(() => ({}))
	]);
	return { gaps, laptimes, lapMatrix, raceTrace, speeds };
};
