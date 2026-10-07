// Team logos inside ECharts text (rich styles) and HTML tooltips.
export type Logos = Record<string, string>; // team id -> data URI

export function logoRich(logos: Logos, size = 14) {
	return Object.fromEntries(
		Object.entries(logos).map(([tid, src]) => [
			tid,
			{ backgroundColor: { image: src }, width: size, height: size }
		])
	);
}

/** Rich text prefix for ECharts labels, empty when the logo is missing. */
export const logoTag = (logos: Logos, tid: string) => (logos[tid] ? `{${tid}|} ` : '');

export const logoImg = (logos: Logos, tid: string) =>
	logos[tid]
		? `<img src="${logos[tid]}" alt="" style="width:14px;height:14px;vertical-align:-3px;margin-right:6px">`
		: '';
