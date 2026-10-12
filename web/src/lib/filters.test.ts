// Run with: node --experimental-strip-types src/lib/filters.test.ts
import assert from 'node:assert/strict';
import { filterEvents, filterLapTimes, filtersFromParams, filtersToParams, type Filters } from './filters.ts';
import type { Stint } from './types.ts';

const f: Filters = { drivers: new Set(['RUS']), laps: [10, 20], compounds: new Set(['SOFT']) };
const stints: Stint[] = [
	{ drv: 'RUS', stint: 1, cmp: 'MEDIUM', from: 1, to: 15, age: 0, new: true },
	{ drv: 'RUS', stint: 2, cmp: 'SOFT', from: 16, to: 30, age: 0, new: true }
];
const laps = filterLapTimes({ RUS: [[9, 100], [12, 101], [17, 99], [25, 98]], ANT: [[17, 99]] }, stints, f);
assert.deepEqual(laps, { RUS: [[17, 99]] });

const events = filterEvents(
	{
		neutral: [],
		msgs: [
			{ lap: 12, kind: 'sc', msg: 'SAFETY CAR', drv: [] },
			{ lap: 12, kind: 'penalty', msg: 'ANT', drv: ['ANT'] },
			{ lap: 30, kind: 'finish', msg: 'FLAG', drv: [] }
		]
	},
	f
);
assert.deepEqual(events.msgs.map((m) => m.kind), ['sc']);
// Shareable URL: only what differs from "everything selected", and back.
const all: Filters = { drivers: new Set(['RUS', 'ANT', 'VER']), laps: [1, 57], compounds: new Set(['SOFT', 'HARD']) };
assert.deepEqual(filtersToParams(all, all), { d: null, l: null, c: null });
const view: Filters = { drivers: new Set(['RUS', 'VER']), laps: [10, 20], compounds: new Set(['SOFT', 'HARD']) };
const params = filtersToParams(view, all);
assert.deepEqual(params, { d: 'RUS,VER', l: '10-20', c: null });
const query = new URLSearchParams(Object.entries(params).filter((e): e is [string, string] => e[1] !== null));
assert.deepEqual(filtersFromParams(query, all), view);
// Junk in a hand-edited URL falls back to "everything".
const junk = filtersFromParams(new URLSearchParams('d=RUS,XXX&l=50-90&c=WET'), all);
assert.deepEqual([...junk.drivers], ['RUS']);
assert.deepEqual(junk.laps, [1, 57]);
assert.equal(junk.compounds.size, 0);

console.log('filters ok');
