# openroomf1

Post-race Formula 1 analysis, as an operation room: [openroomf1.anderson3x11.dev](https://openroomf1.anderson3x11.dev)

After each Grand Prix, a Python pipeline fetches the race data, computes the statistics and writes compact JSON files. A static site turns them into one page per race, split into tabs:

- **Overview**: pole, winner, fastest lap, most overtakes, classification, lap by lap positions, official highlights, race events, championship.
- **Pace**: race trace, gap to the leader or to any driver, lap time heatmap and distribution, fastest lap, ideal lap and top speed.
- **Strategy**: tyre stints, pit stops, fuel corrected tyre degradation, weather.
- **Duels**: every pair of teammates compared.
- **Replay**: every car on the track map, with the running order, tyres and gaps.
- **Radio**: team radios placed on the driver's lap.

Sprints get the same tabs. Qualifying and sprint qualifying get their own: classification by segment with the knockouts, every flying lap against session time, best sectors and ideal lap.

Global filters (drivers, teams, lap range, compound) apply to every tab. Light and dark themes. Seasons 2025 and 2026.

Everything is computed ahead of time: the browser only reads pre-rendered pages, with no database and no calls to the data sources.

## Stack

- **Pipeline**: Python, FastF1, pandas, NumPy.
- **Site**: SvelteKit (static build), ECharts.
- **Hosting**: Caddy in a Docker container, deployed with Coolify.

## Sources

- [FastF1](https://github.com/theOehrly/Fast-F1): timing, laps, stints, track status, race control messages, car positions.
- [Jolpica-F1](https://github.com/jolpica/jolpica-f1): championship standings, circuits.
- [OpenF1](https://openf1.org): team radio metadata.
- F1 live timing archive: official overtakes and pit stop times.
- Formula 1 YouTube channel: official highlights.
- [flag-icons](https://github.com/lipis/flag-icons) (MIT): country flags.
- Team logos from formula1.com. Logos and names belong to their owners.
- Ideas (no code) from [undercut-f1](https://github.com/JustAman62/undercut-f1), [f1-race-replay](https://github.com/IAmTomShaw/f1-race-replay), Armchair Strategist and TracingInsights.

Personal project, unofficial, not associated with Formula 1.
