import { sessionData } from '#lib/server/data.ts';
import type { Speeds } from '#lib/types.ts';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => ({
	speeds: await sessionData<Record<string, Speeds>>(params, params.quali, 'speeds').catch(() => ({}))
});
