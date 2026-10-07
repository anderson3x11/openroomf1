// Schemas of the JSON files written by the pipeline (pipeline/export, pipeline/compute).
// Keep in sync with the Python side.

/** data/SEASON/index.json */
export type SeasonIndex = GpSummary[];

export interface GpSummary {
	round: number;
	slug: string;
	name: string;
	country: string; // country of the Grand Prix name
	date: string; // YYYY-MM-DD
	official?: string; // "FORMULA 1 MOËT & CHANDON BELGIAN GRAND PRIX 2026"
	circuit?: string | null; // "Circuit de Spa-Francorchamps"
	host?: string | null; // country of the circuit: Malaysia for the 2026 Bahrain GP
	flag?: string | null; // ISO 3166 alpha-2 of the host country
}

/** data/SEASON/SLUG/meta.json */
export interface GpMeta extends GpSummary {
	season: number;
	location: string;
	sessions: string[];
	highlights?: string | null; // YouTube video id of the official race highlights
}

/** race/results.json, sorted by finishing position */
export interface ResultRow {
	drv: string; // three-letter code
	num: string;
	name: string;
	team: string;
	tid: string; // team slug, key of the logo file
	color: string | null; // #RRGGBB
	grid: number | null; // null = pit lane start
	pos: number | null;
	cls: string; // classified position, or R / D / W ...
	status: string;
	pts: number;
	gain: number | null; // grid - pos
}

/** race/positions.json: pos[DRV][lap], lap 0 = grid, null = no position */
export interface Positions {
	laps: number;
	pos: Record<string, (number | null)[]>;
}

/** race/strategy.json */
export interface Stint {
	drv: string;
	stint: number;
	cmp: string; // SOFT, MEDIUM, HARD, INTERMEDIATE, WET, UNKNOWN
	from: number;
	to: number;
	age: number | null; // laps already on the tyre at stint start
	new: boolean | null;
}

/** race/gaps.json: gap[DRV][lap] in seconds to the first car to complete that lap */
export interface Gaps {
	laps: number;
	gap: Record<string, (number | null)[]>;
}

export type Neutral = 'sc' | 'vsc' | 'red';

/** race/pitstops.json */
export interface PitStop {
	drv: string;
	lap: number; // in-lap
	lane: number; // seconds between pit entry and pit exit
	stop: number | null; // official stationary time, seconds
	before: number | null; // position at the end of the lap before the in-lap
	after: number | null; // position at the end of the out-lap
	under: Neutral | null;
}

/** race/laptimes.json: DRV -> [lap, seconds][], without lap 1, pit laps and neutralized laps */
export type LapTimes = Record<string, [number, number][]>;

/** race/events.json */
export interface RaceEvents {
	neutral: { kind: Neutral; from: number; to: number }[];
	msgs: {
		lap: number;
		kind: Neutral | 'finish' | 'penalty' | 'investigation';
		msg: string;
		drv: string[];
	}[];
}

/** race/standings.json: championship after this round */
export interface Standings {
	drivers: (StandingRow & { drv: string })[];
	teams: StandingRow[];
}

export interface StandingRow {
	team: string;
	tid: string;
	pos: number | null; // null before a first classification
	pts: number;
	prev: number | null; // position after the previous round
	gain: number; // points scored this round
}

/** race/radios.json: team radio metadata, audio stays on the F1 live timing server */
export interface Radio {
	drv: string;
	lap: number | null; // lap the driver was on, 0 = before the start, null = unknown
	at: string; // HH:MM:SS UTC
	url: string;
}

/** race/summary.json */
export interface Summary {
	fastest: { drv: string; lap: number; t: number } | null; // over every non deleted lap
	overtakes: Record<string, number>; // official F1 overtake count per driver
}

/** race/circuit.json: outline in a WIDTH x h frame, y going down (SVG) */
export interface Circuit {
	w: number;
	h: number;
	path: [number, number][];
	corners: { n: string; x: number; y: number }[];
}

/** race/replay.json: every car every dt seconds of session time, in the circuit frame */
export interface Replay {
	t0: number; // session time of the first frame, seconds
	dt: number;
	n: number; // frames
	cars: Record<string, (number | null)[]>; // flat [x0, y0, x1, y1, ...], null = not shown
	laps: number[]; // session time when the leader completed each lap
	sc?: (number | null)[]; // simulated safety car, same layout as a car, null when not out
}

/** race/laps.json: every lap time (s) and a flag per lap: "p" pit in/out, "n" SC/VSC/red, "" clean */
export interface LapMatrix {
	laps: number;
	t: Record<string, (number | null)[]>;
	f: Record<string, string[]>;
}

/** race/racetrace.json: seconds ahead (+) or behind (-) a car lapping in the field's median lap time */
export interface RaceTrace {
	laps: number;
	trace: Record<string, (number | null)[]>;
}

/** race/weather.json: FastF1 readings between start and flag, lap = leader's fractional lap */
export interface Weather {
	lap: number[];
	air: number[]; // °C
	track: number[]; // °C
	humidity: number[]; // %
	wind: number[]; // m/s
	rain: boolean[];
}

/** race/degradation.json: fuel corrected lap time lost per lap of tyre age, per stint */
export interface Degradation {
	drv: string;
	stint: number;
	cmp: string;
	from: number;
	to: number;
	n: number; // clean laps used for the fit
	deg: number; // s per lap
}

/** race/speeds.json: per driver */
export interface Speeds {
	top: number | null; // speed trap, km/h
	s: (number | null)[]; // best sector times, s
	ideal: number | null; // sum of best sectors
	best: number | null; // best lap
}
