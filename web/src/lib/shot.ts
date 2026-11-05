// Screenshot of one panel, as a PNG, for a video or a post: what is on screen, filters
// included, at twice the screen resolution. Controls marked data-noshot are left out.
import { toBlob } from 'html-to-image';

export async function panelPng(node: HTMLElement): Promise<Blob> {
	const blob = await toBlob(node, {
		pixelRatio: 2,
		backgroundColor: getComputedStyle(node).backgroundColor,
		filter: (n) => !(n instanceof HTMLElement && n.dataset.noshot !== undefined)
	});
	if (!blob) throw new Error('empty screenshot');
	return blob;
}

export function download(blob: Blob, name: string) {
	const a = document.createElement('a');
	a.href = URL.createObjectURL(blob);
	a.download = `${name}.png`;
	a.click();
	URL.revokeObjectURL(a.href);
}

/** To paste straight into a video editor. Not every browser allows images in the clipboard. */
export const copy = (blob: Blob) => navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })]);

export const fileSlug = (text: string) =>
	text
		.toLowerCase()
		.normalize('NFKD')
		.replace(/[^a-z0-9]+/g, '-')
		.replace(/^-|-$/g, '');
