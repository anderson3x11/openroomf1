// The view lives in the URL query (filters, compared drivers): a link reproduces it.
// Browser only: pages are prerendered, without a query.
import { replaceState } from '$app/navigation';
import { page } from '$app/state';

export const readParams = () => new URLSearchParams(window.location.search);

/** Set (or remove, for null) query values, without a navigation. */
export function writeParams(values: Record<string, string | null>) {
	const url = new URL(window.location.href);
	for (const [k, v] of Object.entries(values)) {
		if (v === null) url.searchParams.delete(k);
		else url.searchParams.set(k, v);
	}
	if (url.href !== window.location.href) replaceState(url, page.state);
}
