<script lang="ts">
	import Flag from '#lib/components/Flag.svelte';
	import { hostCountry, shortCircuit, shortName } from '#lib/format.ts';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
</script>

<svelte:head><title>OpenRoom F1</title></svelte:head>

<main>
	{#if data.seasons.length > 1}
		<nav class="label seasons" aria-label="Seasons">
			{#each data.seasons as { season } (season)}<a href="#season-{season}">[ {season} ]</a>{/each}
		</nav>
	{/if}
	{#each data.seasons as { season, gps } (season)}
		<header id="season-{season}">
			<p class="label">[ SEASON ] {gps.length} GRANDS PRIX ANALYSED</p>
			<h1>{season}</h1>
		</header>
		<ol class="gps">
			{#each gps as gp (gp.round)}
				<li>
					<a href="/{season}/{gp.slug}">
						<span class="top">
							<span class="label">[ R{String(gp.round).padStart(2, '0')} ]</span>
							<Flag src={gp.flag ? data.flags[gp.flag] : undefined} country={gp.host ?? gp.country} size={30} />
						</span>
						<span class="name">{shortName(gp.name)}</span>
						<span class="label venue">
							{[shortCircuit(gp.circuit), hostCountry(gp)].filter(Boolean).join(' / ')}
						</span>
						<span class="label date">{gp.date}</span>
					</a>
				</li>
			{/each}
		</ol>
	{:else}
		<p class="label">[ NO GP YET ] Run the pipeline.</p>
	{/each}
</main>

<style>
	main {
		padding: 16px;
		max-width: 1680px;
		margin: 0 auto;
	}
	header {
		margin: 24px 0 20px;
		scroll-margin-top: 16px;
	}
	.seasons {
		display: flex;
		gap: 16px;
		margin-top: 8px;
	}
	.seasons a {
		color: var(--ink-muted);
		text-decoration: none;
	}
	@media (hover: hover) {
		.seasons a:hover {
			color: var(--ink);
		}
	}
	h1 {
		font: 900 clamp(3rem, 12vw, 9rem) / 0.85 var(--sans);
		letter-spacing: -0.04em;
		margin: 8px 0 0;
	}
	.gps {
		list-style: none;
		padding: 0;
		margin: 0;
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
		gap: 1px;
		background: var(--rule);
		border: 1px solid var(--rule);
	}
	a {
		display: grid;
		grid-template-rows: auto auto auto auto;
		gap: 8px;
		padding: 18px 20px;
		background: var(--bg);
		text-decoration: none;
		height: 100%;
	}
	.top {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}
	.name {
		font: 900 34px/1 var(--sans);
		letter-spacing: -0.03em;
		text-transform: uppercase;
		margin-top: 6px;
	}
	.venue {
		color: var(--ink);
	}
	@media (hover: hover) {
		a:hover {
			background: var(--panel);
		}
		a:hover .name {
			color: var(--accent);
		}
	}
</style>
