// Best lap telemetry (about 300 KB), a separate static file fetched by the telemetry tab.
import { listSeasons, raceData, readData } from '#lib/server/data.ts';
import type { SeasonIndex } from '#lib/types.ts';
import type { EntryGenerator, RequestHandler } from './$types';

export const prerender = true;

export const entries: EntryGenerator = async () => {
	const out = [];
	for (const season of await listSeasons()) {
		for (const gp of await readData<SeasonIndex>(String(season), 'index.json')) {
			out.push({ season: String(season), slug: gp.slug });
			if (gp.sessions?.includes('sprint')) out.push({ season: String(season), slug: gp.slug, session: 'sprint' as const });
		}
	}
	return out;
};

export const GET: RequestHandler = async ({ params }) => {
	const tel = await raceData(params, 'telemetry').catch(() => null);
	return new Response(JSON.stringify(tel), { headers: { 'content-type': 'application/json' } });
};
