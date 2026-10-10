// Run with: node --experimental-strip-types src/lib/quali.test.ts
import assert from 'node:assert/strict';
import { fastestBySegment, qualiLines } from './quali.ts';
import type { QualiRow } from './types.ts';

const row = (drv: string, pos: number, q: (number | null)[]) =>
	({ drv, pos, q, num: '', name: drv, team: '', tid: '', color: null }) as QualiRow;
const rows = [
	row('VER', 1, [96.5, 95.7, 95.13]),
	row('ANT', 2, [97.0, 95.9, 95.63]),
	row('LAW', 3, [97.3, 97.02, null]),
	row('COL', 4, [97.18, null, null]), // reached Q2 without a time
	row('PER', 5, [98.9, null, null])
];

assert.deepEqual(fastestBySegment(rows), [96.5, 95.7, 95.13]);
const lines = qualiLines(rows);
assert.deepEqual(lines.map((l) => l.reached), [2, 2, 1, 0, 0]);
assert.deepEqual(lines.map((l) => l.cut), [false, false, true, true, false]);
assert.equal(lines[0].gap, 0);
assert.equal(lines[2].gap?.toFixed(3), '1.320'); // to the fastest Q2 time
assert.equal(lines[4].gap?.toFixed(3), '2.400'); // to the fastest Q1 time
assert.equal(qualiLines([row('X', 1, [null, null, null])])[0].gap, null);
console.log('quali ok');
