import type { Session } from '#lib/types.ts';

/** +3, -2, 0. Empty when unknown. */
export const signed = (n: number | null) => (n === null ? '' : n > 0 ? `+${n}` : String(n));

/** CSS class for a positive / negative change. */
export const trend = (n: number | null) => (n === null || n === 0 ? '' : n > 0 ? 'win' : 'loss');

/** "FORMULA 1 MOËT & CHANDON BELGIAN GRAND PRIX 2026" -> "MOËT & CHANDON BELGIAN GRAND PRIX" */
export const officialTitle = (official: string | undefined, fallback: string) =>
	official ? official.replace(/^FORMULA 1\s+/i, '').replace(/\s+\d{4}$/, '') : fallback;

// Jolpica abbreviates a few country names.
const COUNTRY_NAMES: Record<string, string> = {
	UK: 'United Kingdom',
	USA: 'United States',
	UAE: 'United Arab Emirates'
};

/** "Circuit de Spa-Francorchamps, Belgium", falling back on the GP country. */
export const venue = (gp: { circuit?: string | null; host?: string | null; country: string }) =>
	[gp.circuit, hostCountry(gp)].filter(Boolean).join(', ');

// Circuits whose usual short name cannot be derived from the official one.
const CIRCUIT_SHORT: Record<string, string> = {
	'Circuit of the Americas': 'Austin',
	'Circuit Gilles Villeneuve': 'Montreal',
	'Autodromo Enzo e Dino Ferrari': 'Imola',
	'Autódromo Hermanos Rodríguez': 'Mexico City',
	'Jeddah Corniche Circuit': 'Jeddah',
	'Bahrain International Circuit': 'Sakhir',
	'Las Vegas Strip Street Circuit': 'Las Vegas',
	'Autódromo José Carlos Pace': 'Interlagos'
};

/** "Circuit de Spa-Francorchamps" -> "Spa-Francorchamps", "Circuit Park Zandvoort" -> "Zandvoort". */
export function shortCircuit(circuit: string | null | undefined): string | null {
	if (!circuit) return null;
	if (CIRCUIT_SHORT[circuit]) return CIRCUIT_SHORT[circuit];
	return circuit
		.replace(/^(Circuit Park|Circuit de|Circuit|Autodromo Nazionale di|Autódromo)\s+/, '')
		.replace(/\s+(International Autodrome|International Circuit|Grand Prix Circuit|Street Circuit|City Circuit|Circuit)$/, '')
		.trim();
}

/** Short Grand Prix name: "Dutch Grand Prix" -> "Dutch". */
export const shortName = (name: string) => name.replace(/ Grand Prix$/, '');

/** Host country in full (Jolpica abbreviates a few). */
export const hostCountry = (gp: { host?: string | null; country: string }) => {
	const host = gp.host ?? gp.country;
	return COUNTRY_NAMES[host] ?? host;
};

/** Sessions of a GP as shown on the site, and their URL segment ('' for the race). */
export const SESSION_LABELS: Record<Session, string> = {
	'sprint-quali': 'Sprint quali',
	sprint: 'Sprint',
	quali: 'Qualifying',
	race: 'Race'
};
export const sessionPath = (s: Session) => (s === 'race' ? '' : `/${s}`);
