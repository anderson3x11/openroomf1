/** Quantile with linear interpolation, on a sorted array. */
export function quantile(sorted: number[], q: number): number {
	const pos = (sorted.length - 1) * q;
	const lo = Math.floor(pos);
	const hi = Math.ceil(pos);
	return sorted[lo] + (sorted[hi] - sorted[lo]) * (pos - lo);
}

/** [min, q1, median, q3, max] with whiskers at 1.5 IQR, plus the outliers. */
export function boxStats(values: number[]) {
	const s = [...values].sort((a, b) => a - b);
	const q1 = quantile(s, 0.25);
	const q3 = quantile(s, 0.75);
	const lo = q1 - 1.5 * (q3 - q1);
	const hi = q3 + 1.5 * (q3 - q1);
	const inside = s.filter((v) => v >= lo && v <= hi);
	return {
		box: [inside[0], q1, quantile(s, 0.5), q3, inside[inside.length - 1]],
		outliers: s.filter((v) => v < lo || v > hi)
	};
}

export function formatLap(seconds: number): string {
	const m = Math.floor(seconds / 60);
	return `${m}:${(seconds - m * 60).toFixed(3).padStart(6, '0')}`;
}
