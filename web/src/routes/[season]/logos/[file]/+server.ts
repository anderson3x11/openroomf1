// Team logos downloaded by the pipeline, served as static files.
import { readdir, readFile } from 'node:fs/promises';
import { error } from '@sveltejs/kit';
import { dataPath, listSeasons } from '#lib/server/data.ts';
import type { EntryGenerator, RequestHandler } from './$types';

export const prerender = true;

export const entries: EntryGenerator = async () => {
	const out = [];
	for (const season of await listSeasons()) {
		const files = await readdir(dataPath(String(season), 'logos')).catch(() => [] as string[]);
		out.push(...files.map((file) => ({ season: String(season), file })));
	}
	return out;
};

export const GET: RequestHandler = async ({ params }) => {
	if (!/^[a-z0-9-]+\.webp$/.test(params.file)) error(404);
	const image = await readFile(dataPath(params.season, 'logos', params.file)).catch(() => null);
	if (!image) error(404);
	return new Response(image, { headers: { 'content-type': 'image/webp' } });
};
