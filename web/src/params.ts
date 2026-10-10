// URL segments of the sessions of a GP. Race: /2026/singapore/pace (no segment),
// sprint: /2026/singapore/sprint/pace, qualifying: /2026/singapore/quali, /sprint-quali.
import { defineParams } from '@sveltejs/kit/params';

export const params = defineParams({
	sprint: (param) => (param === 'sprint' ? param : undefined),
	quali: (param) => (param === 'quali' || param === 'sprint-quali' ? param : undefined)
});
