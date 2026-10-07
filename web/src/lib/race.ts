// State shared by the GP layout and its tabs: global filters and the logos of the current theme.
import { createContext } from 'svelte';
import type { Filters } from '#lib/filters.ts';

export interface RaceContext {
	filters: Filters;
	readonly logos: Record<string, string>;
}

export const [getRace, setRace] = createContext<RaceContext>();
