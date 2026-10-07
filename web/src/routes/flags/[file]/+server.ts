// Country flags from flag-icons (MIT), only the ones the seasons use.
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { error } from '@sveltejs/kit';
import { FLAGS_DIR, listSeasons, readData } from '#lib/server/data.ts';
import type { SeasonIndex } from '#lib/types.ts';
import type { EntryGenerator, RequestHandler } from './$types';

export const prerender = true;

export const entries: EntryGenerator = async () => {
	const codes = new Set<string>();
	for (const season of await listSeasons()) {
		for (const gp of await readData<SeasonIndex>(String(season), 'index.json')) {
			if (gp.flag) codes.add(gp.flag);
		}
	}
	return [...codes].map((code) => ({ file: `${code}.svg` }));
};

export const GET: RequestHandler = async ({ params }) => {
	if (!/^[a-z]{2}\.svg$/.test(params.file)) error(404);
	const svg = await readFile(resolve(FLAGS_DIR, params.file)).catch(() => null);
	if (!svg) error(404);
	return new Response(svg, { headers: { 'content-type': 'image/svg+xml' } });
};
