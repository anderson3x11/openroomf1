// Reads the pipeline output at build time (pages are prerendered). The browser never calls an API.
import { readFile, readdir } from 'node:fs/promises';
import { resolve } from 'node:path';

const DATA_DIR = resolve(process.env.DATA_DIR ?? '../data');

export const dataPath = (...parts: string[]) => resolve(DATA_DIR, ...parts);

export async function readData<T>(...parts: string[]): Promise<T> {
	return JSON.parse(await readFile(dataPath(...parts), 'utf-8'));
}

export type ThemedLogos = { dark: Record<string, string>; light: Record<string, string> };

export const FLAGS_DIR = resolve('node_modules/flag-icons/flags/4x3');

/** URLs of the team logos (served by the [season]/logos route): TID.webp for the dark theme,
 * TID-light.webp for the light one. Files, not data URIs: a table repeats a logo on every row,
 * and the browser caches a file once for the whole site. */
export async function readLogos(season: string): Promise<ThemedLogos> {
	const files = await readdir(resolve(DATA_DIR, season, 'logos')).catch(() => [] as string[]);
	const logos: ThemedLogos = { dark: {}, light: {} };
	for (const f of files) {
		const name = f.replace(/\.webp$/, '');
		const url = `/${season}/logos/${f}`;
		if (name.endsWith('-light')) logos.light[name.slice(0, -'-light'.length)] = url;
		else logos.dark[name] = url;
	}
	return logos;
}

/** URLs of host country flags (flag-icons, MIT), served by the flags route. */
export function readFlags(codes: (string | null | undefined)[]): Record<string, string> {
	const valid = codes.filter((c): c is string => !!c && /^[a-z]{2}$/.test(c));
	return Object.fromEntries(valid.map((c) => [c, `/flags/${c}.svg`]));
}

export async function listSeasons(): Promise<number[]> {
	const entries = await readdir(DATA_DIR, { withFileTypes: true }).catch(() => []);
	return entries
		.filter((e) => e.isDirectory() && /^\d{4}$/.test(e.name))
		.map((e) => Number(e.name))
		.sort((a, b) => b - a);
}

/** race/NAME.json of a GP, for the route params of a GP page. */
export const raceData = <T,>(params: { season: string; slug: string }, name: string) =>
	readData<T>(params.season, params.slug, 'race', `${name}.json`);
