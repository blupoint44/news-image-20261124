# news-image-20261124

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/blupoint44/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/blupoint44/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

## The World in One Day, Tuesday 24 November 2026

`main.py` is a pure Python 3 standard-library program — no PIL, no network, no external assets — that draws a complete newspaper front page summarising the world news of Tuesday 24 November 2026 in a single image. It builds everything from scratch: its own raster canvas (a list of rows of RGB tuples), its own 5x7 bitmap font for A–Z, 0–9 and basic punctuation, its own drawing helpers and per-story motif illustrations (a warship under naval drones, a chip, a satellite, court scales, a storm cloud, a medical cross, outbreak spots), and its own PNG encoder built on `zlib` and `struct`. The output is a deterministic 1024x1024 `entry.png`: no randomness and no timestamps, so two runs always produce byte-identical files. The page is headed "THE WORLD IN ONE DAY" with the date line "TUESDAY 24 NOVEMBER 2026", one lead story with an illustration, and six secondary story panels.

Headlines on the page:

- **UKRAINE SAYS IT SANK RUSSIAN WARSHIP OFF LIBYA** — President Zelensky said seven naval drones sank the Russian corvette Merkury at Benghazi port; the UN urged an independent probe into the Benghazi port attacks and Tripoli demanded answers from Kyiv.
- **NVIDIA REINSTATES HUANG AS CEO** — Founder Jensen Huang returned as Nvidia chief after pressure from President Trump; shares surged and the Nasdaq rose 6.51 percent.
- **NATO VOWS TO DEFEND SPACE** — NATO chief Mark Rutte vowed to defend against space threats amid reports that Russia was preparing to launch a nuclear-armed satellite.
- **ICJ: MYANMAR GENOCIDE RULING** — The International Court of Justice found Myanmar committed genocide against the Rohingya, and fourteen countries backed the ruling.
- **COP31 CLIMATE TALKS FAIL** — The UN climate summit ended without a deal after splits over fossil fuels and climate finance.
- **CONGO FIGHTING TRAPS EBOLA** — Heavy fighting near a hospital in Ituri province forced WHO Ebola responders to take cover for more than 24 hours.
- **US LOSES MEASLES-FREE STATUS** — Pennsylvania recorded a ninth measles death in an outbreak across 46 counties, as the United States lost its measles elimination status.

Entered for the make.fun bounty: https://make.fun/bounty/news-image-20261124 — referral: https://make.fun/?ref=cc9ads3n

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=cc9ads3n&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards</sub>
