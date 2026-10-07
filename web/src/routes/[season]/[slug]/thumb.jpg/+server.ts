// Highlights thumbnail, downloaded by the pipeline: the page never loads anything from YouTube.
import { access, readFile } from 'node:fs/promises';
import { dataPath, listSeasons, readData } from '#lib/server/data.ts';
import type { SeasonIndex } from '#lib/types.ts';
import type { EntryGenerator, RequestHandler } from './$types';

export const prerender = true;

/** Only the GPs with a downloaded thumbnail: a missing file would fail the prerender. */
export const entries: EntryGenerator = async () => {
	const out = [];
	for (const season of await listSeasons()) {
		for (const gp of await readData<SeasonIndex>(String(season), 'index.json')) {
			const found = await access(dataPath(String(season), gp.slug, 'thumb.jpg')).then(
				() => true,
				() => false
			);
			if (found) out.push({ season: String(season), slug: gp.slug });
		}
	}
	return out;
};

export const GET: RequestHandler = async ({ params }) => {
	const image = await readFile(dataPath(params.season, params.slug, 'thumb.jpg'));
	return new Response(image, { headers: { 'content-type': 'image/jpeg' } });
};
