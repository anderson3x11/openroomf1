// URL segments of the sessions of a GP. Race: /2026/singapore/pace (no segment),
// sprint: /2026/singapore/sprint/pace. Timed sessions, with the qualifying layout:
// /2026/singapore/quali, /sprint-quali and free practice /fp1, /fp2, /fp3.
import { defineParams } from '@sveltejs/kit/params';

export const params = defineParams({
	sprint: (param) => (param === 'sprint' ? param : undefined),
	quali: (param) =>
		['quali', 'sprint-quali', 'fp1', 'fp2', 'fp3'].includes(param) ? param : undefined
});
