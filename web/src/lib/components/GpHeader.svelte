<script lang="ts">
		import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import type { Circuit, GpMeta, GpSummary, SeasonIndex, Session } from '#lib/types.ts';
	import { officialTitle, SESSION_LABELS, sessionPath, venue } from '#lib/format.ts';
	import CircuitOutline from './CircuitOutline.svelte';
	import Flag from './Flag.svelte';

	let {
		meta,
		season,
		laps,
		circuit,
		flag
	}: { meta: GpMeta; season: SeasonIndex; laps?: number; circuit: Circuit | null; flag?: string } = $props();

	const index = $derived(season.findIndex((g) => g.slug === meta.slug));
	const prev = $derived(season[index - 1]);
	const next = $derived(season[index + 1]);
	const base = $derived(`/${meta.season}/${meta.slug}`);
	// Session and tab of the page: /2026/singapore/sprint/pace -> sprint, sprint/pace.
	const tab = $derived(page.url.pathname.split('/').slice(3).join('/'));
	const session = $derived(
		(meta.sessions.find((s) => s !== 'race' && tab.split('/')[0] === s) ?? 'race') as Session
	);
	// Keep the session and tab when moving to another GP, if it has that session.
	const href = (gp: GpSummary) =>
		session === 'race' || gp.sessions?.includes(session)
			? `/${meta.season}/${gp.slug}${tab ? `/${tab}` : ''}`
			: `/${meta.season}/${gp.slug}`;
	const round = (n: number) => `R${String(n).padStart(2, '0')}`;
	const short = (name: string) => name.replace(/ Grand Prix$/, '');
</script>

{#snippet chevron(d: string)}
	<svg viewBox="0 0 10 10" aria-hidden="true"><path {d} /></svg>
{/snippet}

<div class="head">
	<nav class="label" aria-label="Grands Prix of the season">
		<a class="season" href="/">{meta.season}</a>
		{#if prev}
			<a class="pill" href={href(prev)} title={prev.name}>{@render chevron('M6.5 1.5 3 5l3.5 3.5')}{short(prev.name)}</a>
		{/if}
		<select
			class="pill"
			aria-label="Choose a Grand Prix"
			value={meta.slug}
			onchange={(e) => goto(href(season.find((g) => g.slug === e.currentTarget.value) as GpSummary))}
		>
			{#each season as gp (gp.slug)}
				<option value={gp.slug}>{round(gp.round)} / {short(gp.name)}</option>
			{/each}
		</select>
		{#if next}
			<a class="pill" href={href(next)} title={next.name}>{short(next.name)}{@render chevron('M3.5 1.5 7 5 3.5 8.5')}</a>
		{/if}
	</nav>
	<div class="title">
		<div>
			<p class="label meta">
				<Flag src={flag} country={meta.host ?? meta.country} size={26} />
				{meta.season} / {round(meta.round)} / {venue(meta)} / {meta.date}{laps ? ` / ${laps} LAPS` : ''}
			</p>
			<h1>{short(meta.name)}<br /><span>Grand Prix</span></h1>
			<p class="label official">{officialTitle(meta.official, meta.name)}</p>
		</div>
		{#if circuit}
			<div class="circuit"><CircuitOutline {circuit} label="{meta.location} circuit layout" /></div>
		{/if}
	</div>
	{#if meta.sessions.length > 1}
		<nav class="sessions" aria-label="Sessions of the Grand Prix">
			{#each meta.sessions as s (s)}
				<a class="pill" href="{base}{sessionPath(s)}" aria-current={s === session ? 'page' : undefined}
					>{SESSION_LABELS[s]}</a
				>
			{/each}
		</nav>
	{/if}
</div>

<style>
	.head {
		position: relative;
		color: var(--on-accent);
		background: var(--accent);
		border-radius: 28px;
		margin: 12px 0 0;
		padding: 20px 24px 22px;
	}
	nav {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: 8px;
	}
	nav {
		color: inherit;
	}
	nav a {
		color: inherit;
		text-decoration: none;
	}
	.season {
		font-weight: 700;
		margin-right: 4px;
	}
	/* Every control of the banner, one shape: dark on the red, white when current. */
	.pill {
		display: inline-flex;
		align-items: center;
		gap: 6px;
		height: 34px;
		padding: 0 14px;
		font: 600 12px/1 var(--mono);
		letter-spacing: 0.04em;
		text-transform: uppercase;
		color: inherit;
		background-color: rgb(0 0 0 / 20%);
		border: 0;
		border-radius: 999px;
	}
	.pill svg {
		width: 10px;
		height: 10px;
		fill: none;
		stroke: currentcolor;
		stroke-width: 1.6;
		stroke-linecap: round;
		stroke-linejoin: round;
	}
	select.pill {
		appearance: none;
		cursor: pointer;
		padding-right: 32px;
		background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 10 10'%3E%3Cpath d='M1.5 3.5 5 7l3.5-3.5' fill='none' stroke='white' stroke-width='1.6' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
		background-repeat: no-repeat;
		background-position: right 12px center;
		background-size: 10px;
	}
	option {
		color: var(--ink);
		background: var(--panel);
	}
	.title {
		display: flex;
		justify-content: space-between;
		align-items: flex-end;
		gap: 24px;
	}
	.circuit {
		width: clamp(140px, 24vw, 340px);
		height: clamp(110px, 14vw, 200px);
		flex-shrink: 0;
	}
	.meta {
		margin: 24px 0 0;
		display: flex;
		align-items: center;
		gap: 10px;
		flex-wrap: wrap;
		color: inherit;
	}
	.official {
		margin: 10px 0 0;
		color: inherit;
	}
	/* Many flags are red: the outline keeps them off the banner. */
	.meta :global(.flag) {
		outline-color: var(--on-accent);
	}
	h1 {
		font: 800 clamp(2.4rem, 5.4vw, 5.2rem) / 0.98 var(--sans);
		letter-spacing: -0.02em;
		text-transform: uppercase;
		margin: 14px 0 0;
	}
	h1 span {
		color: #16060a;
	}
	.sessions {
		margin-top: 20px;
		gap: 4px;
	}
	.sessions a[aria-current='page'] {
		color: var(--accent);
		background: var(--on-accent);
	}
	@media (hover: hover) {
		.pill:hover {
			background-color: rgb(0 0 0 / 34%);
		}
		.sessions a[aria-current='page']:hover {
			background: var(--on-accent);
		}
	}
	/* From 1100px the track takes the whole height of the banner. */
	@media (min-width: 1100px) {
		.circuit {
			position: absolute;
			top: 24px;
			right: 32px;
			bottom: 24px;
			width: min(38%, 620px);
			height: auto;
		}
	}
	@media (max-width: 700px) {
		.head {
			border-radius: 22px;
			padding: 16px;
		}
		.circuit {
			display: none;
		}
		select {
			font-size: 16px; /* avoids iOS zoom on focus */
		}
	}
</style>
