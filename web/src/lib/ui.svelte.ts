// Theme preference (auto / light / dark), resolved to the theme actually displayed.
// Charts read ui.theme while building their options, so they rebuild on theme change.
export type ThemePref = 'auto' | 'light' | 'dark';

export type Da = '' | 'livery' | 'hub' | 'tower';

export const ui = $state({ pref: 'auto' as ThemePref, theme: 'dark' as 'light' | 'dark', da: '' as Da });

const KEY = 'openroom-theme';

/** Art direction under test (branch only): ?da=livery|hub|tower, '' is the current site. */
export function setDa(da: Da) {
	ui.da = da;
	document.documentElement.dataset.da = da;
	const url = new URL(window.location.href);
	if (da) url.searchParams.set('da', da);
	else url.searchParams.delete('da');
	history.replaceState(history.state, '', url);
}

/** A status label: bracketed in the terminal look of the current site, plain otherwise. */
export const tag = (text: string | number) => (ui.da ? String(text) : `[ ${text} ]`);

function apply() {
	const dark = window.matchMedia('(prefers-color-scheme: dark)').matches;
	ui.theme = ui.pref === 'auto' ? (dark ? 'dark' : 'light') : ui.pref;
	document.documentElement.dataset.theme = ui.theme;
}

export function initTheme() {
	try {
		ui.pref = (localStorage.getItem(KEY) as ThemePref) ?? 'auto';
	} catch {
		// Storage can be blocked: fall back to the system preference.
	}
	const da = new URLSearchParams(window.location.search).get('da');
	if (da === 'livery' || da === 'hub' || da === 'tower') setDa(da);
	apply();
	const mq = window.matchMedia('(prefers-color-scheme: dark)');
	mq.addEventListener('change', apply);
	return () => mq.removeEventListener('change', apply);
}

export function cycleTheme() {
	const order: ThemePref[] = ['auto', 'light', 'dark'];
	ui.pref = order[(order.indexOf(ui.pref) + 1) % order.length];
	try {
		localStorage.setItem(KEY, ui.pref);
	} catch {
		// Not persisted, still applied for this visit.
	}
	apply();
}
