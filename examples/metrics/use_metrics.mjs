// Pass the emitted ESM file as the first argument.
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';
import assert from 'node:assert/strict';
const metrics = await import(pathToFileURL(resolve(process.argv[2] || 'build/js/metrics.mjs')));
const samples = [42, 95, 380];
assert.equal(metrics.average(samples), 517 / 3);
assert.equal(metrics.minimum(samples), 42);
assert.equal(metrics.maximum(samples), 380);
assert.equal(Number(metrics.count_over(samples, 200)), 1);
console.log(JSON.stringify({ samples: Number(metrics.sample_count(samples)), average_ms: metrics.average(samples), over_200_ms: Number(metrics.count_over(samples, 200)) }));
