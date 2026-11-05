<script lang="ts">
	import { tick, type Snippet } from 'svelte';
	import { capture } from '#lib/capture.svelte.ts';
	import { getRace } from '#lib/race.ts';
	import { copy, download, fileSlug, panelPng } from '#lib/shot.ts';

	let {
		title,
		desc,
		wide = false,
		actions,
		children
	}: { title: string; desc?: string; wide?: boolean; actions?: Snippet; children: Snippet } = $props();

	const race = getRace();
	let el: HTMLElement;
	// While capturing, the panel shows its caption (GP, session, filters) and the site address.
	let capturing = $state(false);
	let status = $state('');

	async function shoot(then: (blob: Blob) => unknown, done: string) {
		capturing = capture.on = true;
		await tick();
		try {
			await then(await panelPng(el));
			status = done;
		} catch (e) {
			console.error('screenshot failed', e);
			status = 'FAILED';
		} finally {
			capturing = capture.on = false;
			setTimeout(() => (status = ''), 2000);
		}
	}
	const save = () => shoot((b) => download(b, `${race.shot.file}-${fileSlug(title)}`), 'SAVED');
	const clip = () => shoot(copy, 'COPIED');
</script>

<section class="panel" class:wide class:capturing bind:this={el}>
	{#if capturing}<div class="label caption">{race.shot.caption}</div>{/if}
	<header>
		<div>
			<h2>// {title}</h2>
			{#if desc && !capturing}<p>{desc}</p>{/if}
		</div>
		<div class="actions" data-noshot>
			{#if actions}{@render actions()}{/if}
			<span class="shot label">
				{#if status}{status}{:else}
					<button onclick={save} title="Save this panel as a PNG image">[ PNG ]</button>
					<button onclick={clip} title="Copy this panel as an image">[ COPY ]</button>
				{/if}
			</span>
		</div>
	</header>
	{@render children()}
	{#if capturing}<div class="label credit">OPENROOMF1.ANDERSON3X11.DEV</div>{/if}
</section>

<style>
	.panel {
		background: var(--bg);
		padding: 20px;
		min-width: 0;
	}
	.wide {
		grid-column: 1 / -1;
	}
	/* In the page grid a panel stretches to its neighbor: an image keeps its own height. */
	.capturing {
		align-self: start;
	}
	header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 16px;
		flex-wrap: wrap;
		margin-bottom: 16px;
	}
	.actions {
		display: flex;
		align-items: center;
		gap: 12px;
		flex-wrap: wrap;
	}
	.shot button {
		font: inherit;
		color: var(--ink-muted);
		background: none;
		border: none;
		padding: 0;
		cursor: pointer;
	}
	.shot {
		display: flex;
		gap: 8px;
	}
	.caption {
		margin: 0 0 14px;
		color: var(--ink);
	}
	.credit {
		margin: 14px 0 0;
		text-align: right;
	}
	@media (hover: hover) {
		.shot button:hover {
			color: var(--ink);
		}
	}
	h2 {
		font: 700 14px/1.2 var(--mono);
		letter-spacing: 0.08em;
		text-transform: uppercase;
		margin: 0;
	}
	p {
		font: 13px/1.45 var(--mono);
		color: var(--ink-muted);
		margin: 6px 0 0;
		max-width: 90ch;
	}
</style>
