// Theme preference (auto / light / dark), resolved to the theme actually displayed.
// Charts read ui.theme while building their options, so they rebuild on theme change.
export type ThemePref = 'auto' | 'light' | 'dark';

export const ui = $state({ pref: 'auto' as ThemePref, theme: 'dark' as 'light' | 'dark' });

const KEY = 'openroom-theme';

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
