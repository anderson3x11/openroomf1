import { listSeasons, readData, readFlags } from '#lib/server/data.ts';
import type { SeasonIndex } from '#lib/types.ts';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
	const seasons = await Promise.all(
		(await listSeasons()).map(async (season) => ({
			season,
			gps: await readData<SeasonIndex>(String(season), 'index.json')
		}))
	);
	const flags = readFlags(seasons.flatMap((s) => s.gps.map((gp) => gp.flag)));
	return { seasons, flags };
};
