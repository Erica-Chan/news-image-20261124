# news-image-20261124

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/Erica-Chan/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/Erica-Chan/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

One image summing up the world's news of Tuesday, 24 November 2026: 38 stories across 9 regions. Three large leads: a Houthi missile hits Riyadh's tallest tower, wounding 11; Nvidia gives back $240bn as the AI rally fizzles a day after its 31.5% surge; and a Russian strike kills 2 and wounds 40 in Zaporizhzhia. Thirteen medium cards, each with its own code-drawn illustration and a certainty badge (CONFIRMED / REPORTED / CLAIM / PENDING / FORECAST): CAS hands Senegal back the AFCON title, NATO vows to defend space, Russia warns Estonia of war, a tally puts Russian war dead past 700,000, Vance and Rubio meet Qatar's PM, Iran's rial plunges, Russian jets enter Korea's air-defence zone, China probes a Politburo member, Germany gets Ukraine's Delta system, Iraq seizes Kurdish oilfields, fighting traps Ebola medics in DR Congo, Spain amnesties Puigdemont, and the UK sanctions Houthi leaders — plus a by-the-numbers panel, a UTC timeline, 22 more stories with certainty dots, a world map with numbered pins, and a date-check box naming stories left out because they happened on earlier days.

The poster is drawn by `compose_poster.py` (PIL; crisp text over flat vector illustrations drawn in code — no photographs, no AI images) from the sourced, dated story list in `stories.json`, and shipped as `entry.png`. `main.ts` (Node 22, standard library only) copies it to `/output/entry.png`, so two runs write identical bytes with no network.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=96p1ekwa&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards</sub>
