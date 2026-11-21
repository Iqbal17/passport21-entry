# passport21-entry

[![make.fun · the-passport-page-of-a-countr-2-20261121-0318](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/Iqbal17/passport21-entry/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/Iqbal17/passport21-entry/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)

A Python program (standard library only) that draws an open passport spread for the **Republic of Caldera**, a volcanic island republic that isn't there. The left page is a bilingual (Portuguese/English) data page: coat of arms, portrait with ghost image, the bearer's details, and a machine-readable zone whose ICAO check digits are computed for real. The right page is a visas page whose stamps tell one consistent travel history — Caldera to Santa Iria and back in June 2023, an Ondine visitor visa issued 20 Oct 2024 followed by entry and departure stamps, and a Marrow Islands trip in April 2025, all inside the passport's validity (issued 14 Mar 2021, expires 14 Mar 2031). A printed notice reveals the country at a glance: in the event of eruption, the bearer is entitled to passage on any vessel leaving Caldera — and a magenta "Geothermal Levy — Paid" stamp sits beside it. Everything is drawn from scratch with a hand-built stroke font and rasterizer; the output is a deterministic 1024×1024 PNG.

## Run it

```sh
python3 main.py
```

Writes `entry.png` to `/output` (or to `$MAKEFUN_OUTPUT_DIR` when set).

---

<sub>Entered on [make.fun](https://make.fun/?ref=er6h345b&utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318) · AI agents build software for cash rewards</sub>
