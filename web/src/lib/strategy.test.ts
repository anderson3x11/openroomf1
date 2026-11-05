// Run with: node --experimental-strip-types src/lib/strategy.test.ts
import assert from 'node:assert/strict';
import { strategyRows } from './strategy.ts';
import type { Driver, Stint } from './types.ts';

const driver = { drv: 'VER' } as Driver;
const stint = (n: number, from: number, to: number) =>
	({ drv: 'VER', stint: n, cmp: 'SOFT', from, to, age: 0, new: true }) as Stint;
const stints = [stint(1, 1, 25), stint(2, 26, 50), stint(3, 51, 100)];

const [row] = strategyRows([driver], stints, [1, 100]);
assert.deepEqual(row.marks, [{ lap: 25, x: 25 }, { lap: 50, x: 50 }]); // no disc after the last stint
assert.equal(row.last, 100);
assert.deepEqual(row.segments.map((s) => [s.left, s.width]), [[0, 25], [25, 25], [50, 50]]);

// A lap range keeps what is inside it, on the full width.
const [zoom] = strategyRows([driver], stints, [26, 50]);
assert.equal(zoom.segments.length, 1);
assert.deepEqual([zoom.segments[0].left, zoom.segments[0].width], [0, 100]);
assert.deepEqual(zoom.marks.map((m) => m.lap), [50]);

// Stops one lap apart (red flag): one disc, they would overlap.
const close = [stint(1, 1, 44), stint(2, 45, 45), stint(3, 46, 100)];
assert.deepEqual(strategyRows([driver], close, [1, 100])[0].marks.map((m) => m.lap), [44]);

assert.equal(strategyRows([{ drv: 'XXX' } as Driver], stints, [1, 100])[0].last, null); // no data
console.log('strategy ok');
