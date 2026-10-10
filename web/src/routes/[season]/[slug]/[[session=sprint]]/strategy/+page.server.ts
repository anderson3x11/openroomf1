import { raceData } from '#lib/server/data.ts';
import type { Degradation, PitStop, Weather } from '#lib/types.ts';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
	const [pitstops, degradation, weather] = await Promise.all([
		raceData<PitStop[]>(params, 'pitstops'),
		raceData<Degradation[]>(params, 'degradation').catch(() => []),
		raceData<Weather>(params, 'weather').catch(() => null)
	]);
	return { pitstops, degradation, weather };
};
