<script lang="ts">
	let { src, country, size = 22 }: { src?: string; country: string; size?: number } = $props();
</script>

{#if src}<img class="flag" {src} alt="Flag of {country}" style:height="{size * 0.75}px" style:width="{size}px" />{/if}

<style>
	.flag {
		display: inline-block;
		object-fit: cover;
		outline: 1px solid var(--rule);
		vertical-align: middle;
		flex-shrink: 0;
	}
</style>
