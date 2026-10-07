import { raceData } from '#lib/server/data.ts';
import type { Gaps } from '#lib/types.ts';
import type { PageServerLoad } from './$types';

/** The replay itself is fetched by the page from replay.json: only the gaps are needed here. */
export const load: PageServerLoad = async ({ params }) => ({ gaps: await raceData<Gaps>(params, 'gaps') });
