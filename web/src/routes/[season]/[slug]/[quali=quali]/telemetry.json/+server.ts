// Best lap telemetry of a qualifying or practice session, fetched by its telemetry tab.
import { listSeasons, readData, sessionData } from '#lib/server/data.ts';
import type { SeasonIndex } from '#lib/types.ts';
import type { EntryGenerator, RequestHandler } from './$types';

export const prerender = true;

export const entries: EntryGenerator = async () => {
	const out = [];
	for (const season of await listSeasons()) {
		for (const gp of await readData<SeasonIndex>(String(season), 'index.json')) {
			for (const s of gp.sessions ?? []) {
				if (s !== 'race' && s !== 'sprint') out.push({ season: String(season), slug: gp.slug, quali: s });
			}
		}
	}
	return out;
};

export const GET: RequestHandler = async ({ params }) => {
	const tel = await sessionData(params, params.quali, 'telemetry').catch(() => null);
	return new Response(JSON.stringify(tel), { headers: { 'content-type': 'application/json' } });
};
