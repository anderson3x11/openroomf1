<script lang="ts">
	// F1 blocks its videos on other sites: a link card to YouTube, with the thumbnail served
	// from our own files (no request to YouTube until the viewer clicks).
	let { id, thumb, title }: { id: string; thumb: string | null; title: string } = $props();
</script>

<a class="card" href="https://www.youtube.com/watch?v={id}" target="_blank" rel="noopener noreferrer">
	<span class="frame">
		{#if thumb}<img src={thumb} alt="" loading="lazy" />{/if}
		<svg class="yt" viewBox="0 0 68 48" aria-hidden="true">
			<path d="M66.5 7.7a8.5 8.5 0 0 0-6-6C55.2.3 34 .3 34 .3s-21.2 0-26.5 1.4a8.5 8.5 0 0 0-6 6C.1 13 .1 24 .1 24s0 11 1.4 16.3a8.5 8.5 0 0 0 6 6C12.8 47.7 34 47.7 34 47.7s21.2 0 26.5-1.4a8.5 8.5 0 0 0 6-6C67.9 35 67.9 24 67.9 24s0-11-1.4-16.3z" fill="#f00" />
			<path d="M27 34.3 44.8 24 27 13.7z" fill="#fff" />
		</svg>
	</span>
	<span class="caption">
		<b>{title}</b>
		<span class="label">[ WATCH ON YOUTUBE ]</span>
	</span>
</a>

<style>
	.card {
		display: grid;
		gap: 10px;
		text-decoration: none;
		color: var(--ink);
	}
	.frame {
		position: relative;
		aspect-ratio: 16 / 9;
		background: var(--panel);
		border: 1px solid var(--rule);
		display: grid;
		place-items: center;
		overflow: hidden;
	}
	img {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		object-fit: cover;
		transition: transform 200ms ease-out;
	}
	.yt {
		position: relative;
		width: 68px;
		height: 48px;
		filter: drop-shadow(0 2px 6px rgb(0 0 0 / 0.4));
	}
	.caption {
		display: flex;
		justify-content: space-between;
		gap: 12px;
		flex-wrap: wrap;
		font: 14px var(--mono);
	}
	@media (hover: hover) {
		.card:hover img {
			transform: scale(1.02);
		}
		.card:hover .label {
			color: var(--ink);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		img {
			transition: none;
		}
	}
</style>
