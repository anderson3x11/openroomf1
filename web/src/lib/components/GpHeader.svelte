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

<div class="head">
	<nav class="label" aria-label="Grands Prix of the season">
		<a href="/">{meta.season}</a>
		<a class="step" href={prev ? href(prev) : undefined} aria-disabled={!prev} title={prev?.name}
			>&lt; {prev ? short(prev.name) : ''}</a
		>
		<select
			aria-label="Choose a Grand Prix"
			value={meta.slug}
			onchange={(e) => goto(href(season.find((g) => g.slug === e.currentTarget.value) as GpSummary))}
		>
			{#each season as gp (gp.slug)}
				<option value={gp.slug}>{round(gp.round)} / {short(gp.name)}</option>
			{/each}
		</select>
		<a class="step" href={next ? href(next) : undefined} aria-disabled={!next} title={next?.name}
			>{next ? short(next.name) : ''} &gt;</a
		>
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
				<a class="label" href="{base}{sessionPath(s)}" aria-current={s === session ? 'page' : undefined}
					>{SESSION_LABELS[s]}</a
				>
			{/each}
		</nav>
	{/if}
</div>

<style>
	.head {
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
	.step {
		border: 1px solid currentcolor;
		border-radius: 999px;
		padding: 6px 12px;
	}
	.step[aria-disabled='true'] {
		opacity: 0.6;
		pointer-events: none;
	}
	select {
		font: 600 13px var(--mono);
		letter-spacing: 0.04em;
		text-transform: uppercase;
		color: inherit;
		background: transparent;
		border: 1px solid currentcolor;
		padding: 5px 10px;
	}
	option {
		color: #14141a;
	}
	.title {
		display: flex;
		justify-content: space-between;
		align-items: flex-end;
		gap: 24px;
	}
	.circuit {
		width: clamp(140px, 22vw, 340px);
		height: clamp(110px, 13vw, 200px);
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
	.sessions a {
		border: 1px solid currentcolor;
		border-radius: 999px;
		padding: 8px 14px;
		color: inherit;
	}
	.sessions a[aria-current='page'] {
		color: var(--accent);
		background: var(--on-accent);
		border-color: var(--on-accent);
	}
	@media (hover: hover) {
		.step:hover,
		.sessions a:hover {
			background: rgb(255 255 255 / 16%);
		}
		.sessions a[aria-current='page']:hover {
			background: var(--on-accent);
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
