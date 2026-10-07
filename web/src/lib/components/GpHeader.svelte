<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import type { Circuit, GpMeta, SeasonIndex } from '#lib/types.ts';
	import { officialTitle, venue } from '#lib/format.ts';
	import CircuitOutline from './CircuitOutline.svelte';
	import Flag from './Flag.svelte';

	let {
		meta,
		season,
		laps,
		circuit,
		flag
	}: { meta: GpMeta; season: SeasonIndex; laps: number; circuit: Circuit | null; flag?: string } = $props();

	const index = $derived(season.findIndex((g) => g.slug === meta.slug));
	const prev = $derived(season[index - 1]);
	const next = $derived(season[index + 1]);
	// Keep the current tab when moving to another GP.
	const tab = $derived(page.url.pathname.split('/').slice(3).join('/'));
	const href = (slug: string) => `/${meta.season}/${slug}${tab ? `/${tab}` : ''}`;
	const round = (n: number) => `R${String(n).padStart(2, '0')}`;
	const short = (name: string) => name.replace(/ Grand Prix$/, '');
</script>

<div class="head">
	<nav class="label" aria-label="Grands Prix of the season">
		<a href="/">[ {meta.season} ]</a>
		<a class="step" href={prev ? href(prev.slug) : undefined} aria-disabled={!prev} title={prev?.name}
			>&lt; {prev ? short(prev.name) : ''}</a
		>
		<select
			aria-label="Choose a Grand Prix"
			value={meta.slug}
			onchange={(e) => goto(href(e.currentTarget.value))}
		>
			{#each season as gp (gp.slug)}
				<option value={gp.slug}>{round(gp.round)} / {short(gp.name)}</option>
			{/each}
		</select>
		<a class="step" href={next ? href(next.slug) : undefined} aria-disabled={!next} title={next?.name}
			>{next ? short(next.name) : ''} &gt;</a
		>
	</nav>
	<div class="title">
		<div>
			<p class="label meta">
				<Flag src={flag} country={meta.host ?? meta.country} size={26} />
				[ {meta.season} / {round(meta.round)} ] {venue(meta)} / {meta.date} / {laps} LAPS
			</p>
			<h1>{short(meta.name)}<br /><span>Grand Prix</span></h1>
			<p class="label official">{officialTitle(meta.official, meta.name)}</p>
		</div>
		{#if circuit}
			<div class="circuit"><CircuitOutline {circuit} label="{meta.location} circuit layout" /></div>
		{/if}
	</div>
</div>

<style>
	.head {
		padding: 20px 0 16px;
	}
	nav {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: 8px;
	}
	nav a {
		color: var(--ink-muted);
		text-decoration: none;
	}
	.step {
		border: 1px solid var(--rule);
		padding: 6px 10px;
	}
	.step[aria-disabled='true'] {
		opacity: 0.3;
		pointer-events: none;
	}
	select {
		font: 500 13px var(--mono);
		letter-spacing: 0.05em;
		text-transform: uppercase;
		color: var(--ink);
		background: var(--bg);
		border: 1px solid var(--rule);
		border-radius: 0;
		padding: 5px 8px;
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
	}
	.official {
		margin: 10px 0 0;
	}
	h1 {
		font: 900 clamp(2.75rem, 7vw, 6.5rem) / 0.86 var(--sans);
		letter-spacing: -0.05em;
		text-transform: uppercase;
		margin: 12px 0 0;
	}
	h1 span {
		color: var(--accent);
	}
	@media (hover: hover) {
		nav a:hover {
			color: var(--ink);
			border-color: var(--ink-muted);
		}
	}
	@media (max-width: 700px) {
		.circuit {
			display: none;
		}
		select {
			font-size: 16px; /* avoids iOS zoom on focus */
		}
	}
</style>
