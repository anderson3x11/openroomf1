import { access } from 'node:fs/promises';
import { dataPath, raceData } from '#lib/server/data.ts';
import type { Standings, Summary } from '#lib/types.ts';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
	// Standings and highlights belong to the race, not to the sprint.
	const race = !params.session;
	const [standings, summary, hasThumb] = await Promise.all([
		race ? raceData<Standings>(params, 'standings') : null,
		raceData<Summary>(params, 'summary'),
		race &&
			access(dataPath(params.season, params.slug, 'thumb.jpg')).then(
			() => true,
			() => false
		)
	]);
	return { standings, summary, hasThumb, race };
};
