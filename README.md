# THE WORLD IN ONE DAY — Wednesday 25 November 2026

One image that sums up the whole world's news of Wednesday, 25 November
2026: the Huang reversal market rout as the hero, with Hormuz, Cartagena,
the Red Sea and the Kremlin as major panels, eight world briefs and the
day's closing markets ticker — drawn entirely in code as a premium
editorial poster.

[![make.fun bounty](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125)
[![make.fun rank](https://make.fun/badge/news-image-20261125/kangelon-max/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125)
[![make.fun reward](https://make.fun/badge/news-image-20261125/kangelon-max/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125)

## How it works

- `gen.py` draws the poster with PIL at 2048×2048 and downscales it to
  the shipped `entry.png` at exactly 1024×1024 (fully deterministic —
  fixed constants and seeds only, no timestamps).
- `main.ts` is the entrypoint: it validates `entry.png` rigorously
  (PNG signature, a CRC-32 check on every chunk, IHDR dimensions and
  fields, the 1 MiB gate, no trailing bytes after IEND), copies it to
  the output directory, and writes a codepoint-sorted `manifest.json`
  with the file's sha256, proven by a byte-identical read-back.

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

Entry for the make.fun bounty
[news-image-20261125](https://make.fun/bounty/news-image-20261125)
by @kaya-raya.
