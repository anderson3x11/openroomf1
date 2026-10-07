import { raceData } from '#lib/server/data.ts';
import type { Radio } from '#lib/types.ts';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => ({
	radios: await raceData<Radio[]>(params, 'radios').catch(() => [])
});
