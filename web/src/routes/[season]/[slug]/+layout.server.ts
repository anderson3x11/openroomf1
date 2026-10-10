import { readData, readFlags, readLogos, sessionData } from '#lib/server/data.ts';
import type { Circuit, GpMeta, SeasonIndex } from '#lib/types.ts';
import type { LayoutServerLoad } from './$types';

/** What every session of the GP needs: header, logos. The track map comes from the race. */
export const load: LayoutServerLoad = async ({ params }) => {
	const [meta, season, circuit, logos] = await Promise.all([
		readData<GpMeta>(params.season, params.slug, 'meta.json'),
		readData<SeasonIndex>(params.season, 'index.json'),
		sessionData<Circuit>(params, 'race', 'circuit').catch(() => null),
		readLogos(params.season)
	]);
	return { flags: readFlags([meta.flag]), meta, season, circuit, logos };
};
