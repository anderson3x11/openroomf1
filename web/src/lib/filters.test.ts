// Run with: node --experimental-strip-types src/lib/filters.test.ts
import assert from 'node:assert/strict';
import { filterEvents, filterLapTimes, type Filters } from './filters.ts';
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
console.log('filters ok');
