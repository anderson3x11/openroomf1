// The replay (about 1 MB per GP) is a separate static file, fetched only by the replay tab.
import { listSeasons, readData } from '#lib/server/data.ts';
import type { SeasonIndex } from '#lib/types.ts';
import type { EntryGenerator, RequestHandler } from './$types';

export const prerender = true;

export const entries: EntryGenerator = async () => {
	const out = [];
	for (const season of await listSeasons()) {
		for (const gp of await readData<SeasonIndex>(String(season), 'index.json')) {
			out.push({ season: String(season), slug: gp.slug });
		}
	}
	return out;
};

export const GET: RequestHandler = async ({ params }) => {
	const replay = await readData(params.season, params.slug, 'race', 'replay.json').catch(() => null);
	return new Response(JSON.stringify(replay), { headers: { 'content-type': 'application/json' } });
};
