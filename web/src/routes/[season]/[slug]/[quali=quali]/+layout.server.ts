import { sessionData } from '#lib/server/data.ts';
import type { QualiLaps, QualiRow, Session } from '#lib/types.ts';
import type { LayoutServerLoad } from './$types';

/** Qualifying or sprint qualifying: classification and flying laps (small, both tabs use them). */
export const load: LayoutServerLoad = async ({ params }) => {
	const [results, laps] = await Promise.all([
		sessionData<QualiRow[]>(params, params.quali, 'results'),
		sessionData<QualiLaps>(params, params.quali, 'laps')
	]);
	return { results, laps, session: params.quali as Session };
};
