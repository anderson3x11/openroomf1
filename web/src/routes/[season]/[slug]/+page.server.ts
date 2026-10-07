import { access } from 'node:fs/promises';
import { dataPath, raceData } from '#lib/server/data.ts';
import type { Standings, Summary } from '#lib/types.ts';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
	const [standings, summary, hasThumb] = await Promise.all([
		raceData<Standings>(params, 'standings'),
		raceData<Summary>(params, 'summary'),
		access(dataPath(params.season, params.slug, 'thumb.jpg')).then(
			() => true,
			() => false
		)
	]);
	return { standings, summary, hasThumb };
};
