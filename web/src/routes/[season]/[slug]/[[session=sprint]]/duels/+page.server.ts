import { raceData } from '#lib/server/data.ts';
import type { LapTimes, Speeds } from '#lib/types.ts';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
	const [laptimes, speeds] = await Promise.all([
		raceData<LapTimes>(params, 'laptimes'),
		raceData<Record<string, Speeds>>(params, 'speeds').catch(() => ({}))
	]);
	return { laptimes, speeds };
};
