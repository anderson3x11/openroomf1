import { dataPath, raceData, readData, readFlags, readLogos } from '#lib/server/data.ts';
import type {
	Circuit,
	GpMeta,
	Positions,
	RaceEvents,
	Radio,
	ResultRow,
	SeasonIndex,
	Stint
} from '#lib/types.ts';
import type { LayoutServerLoad } from './$types';

/** What every tab needs: header, filters, logos. Each tab loads its own data on top (its
 * +page.server.ts), so a page does not carry the data of the five others. */
export const load: LayoutServerLoad = async ({ params }) => {
	const [meta, season, results, positions, strategy, events, radios, circuit, logos] = await Promise.all([
		readData<GpMeta>(params.season, params.slug, 'meta.json'),
		readData<SeasonIndex>(params.season, 'index.json'),
		raceData<ResultRow[]>(params, 'results'),
		raceData<Positions>(params, 'positions'),
		raceData<Stint[]>(params, 'strategy'),
		raceData<RaceEvents>(params, 'events'),
		raceData<Radio[]>(params, 'radios').catch(() => []),
		raceData<Circuit>(params, 'circuit').catch(() => null),
		readLogos(params.season)
	]);
	return {
		flags: readFlags([meta.flag]),
		meta,
		season,
		results,
		positions,
		strategy,
		events,
		radioCount: radios.length,
		circuit,
		logos
	};
};

