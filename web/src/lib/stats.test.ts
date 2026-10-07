// Run with: node --experimental-strip-types src/lib/stats.test.ts
import assert from 'node:assert/strict';
import { boxStats, formatLap, quantile } from './stats.ts';

assert.equal(quantile([1, 2, 3, 4], 0.5), 2.5);
const { box, outliers } = boxStats([100, 101, 102, 103, 104, 130]);
assert.deepEqual(outliers, [130]);
assert.equal(box[0], 100);
assert.equal(box[4], 104);
assert.equal(formatLap(105.2), '1:45.200');
console.log('stats ok');
