<script lang="ts">
	import favicon from '#lib/assets/favicon.svg';
	import { cycleTheme, initTheme, ui } from '#lib/ui.svelte.ts';
	import '../app.css';
	import type { LayoutProps } from './$types';

	let { children }: LayoutProps = $props();

	$effect(() => initTheme());

	const THEME_LABELS = { auto: 'AUTO', light: 'LIGHT', dark: 'DARK' };
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<header class="bar">
	<a href="/" class="label brand">[ OPENROOM / F1 ]</a>
	<button class="label theme" onclick={cycleTheme} title="Switch theme">
		THEME: {THEME_LABELS[ui.pref]}
	</button>
</header>

{@render children()}

<footer class="label">
	UNOFFICIAL SITE, NOT AFFILIATED WITH FORMULA 1. TEAM LOGOS AND NAMES BELONG TO THEIR OWNERS.
	DATA: FASTF1, JOLPICA, OPENF1, F1 LIVE TIMING. VIDEOS: FORMULA 1 YOUTUBE CHANNEL. FLAGS: FLAG-ICONS.
</footer>

<style>
	.bar {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 16px;
		padding: 8px 16px;
		border-bottom: 1px solid var(--rule);
	}
	.brand {
		color: var(--ink);
		text-decoration: none;
	}
	.theme {
		background: none;
		border: 1px solid var(--rule);
		padding: 4px 8px;
		cursor: pointer;
		touch-action: manipulation;
	}
	@media (hover: hover) {
		.theme:hover {
			color: var(--ink);
			border-color: var(--ink-muted);
		}
	}
	footer {
		padding: 24px 16px;
		border-top: 1px solid var(--rule);
		font-size: 10px;
	}
</style>
