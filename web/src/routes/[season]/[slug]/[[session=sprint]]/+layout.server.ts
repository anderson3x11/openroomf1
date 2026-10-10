import { raceData } from '#lib/server/data.ts';
import type { Positions, RaceEvents, Radio, ResultRow, Stint } from '#lib/types.ts';
import type { LayoutServerLoad } from './$types';

/** What every tab of the race (or the sprint) needs: filters, tabs. Each tab loads its own
 * data on top (its +page.server.ts), so a page does not carry the data of the five others. */
export const load: LayoutServerLoad = async ({ params }) => {
	const [results, positions, strategy, events, radios] = await Promise.all([
		raceData<ResultRow[]>(params, 'results'),
		raceData<Positions>(params, 'positions'),
		raceData<Stint[]>(params, 'strategy'),
		raceData<RaceEvents>(params, 'events'),
		raceData<Radio[]>(params, 'radios').catch(() => [])
	]);
	// The URL segment of the session, '' for the race: /2026/singapore + SEGMENT + /pace.
	const segment = params.session ? `/${params.session}` : '';
	return { results, positions, strategy, events, radioCount: radios.length, segment };
};
