![make.fun](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6.svg)
![rank](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/aurorabelle788/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6-v1/rank.svg)
![reward](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/aurorabelle788/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6-v1/reward.svg)

# Meme Sprint 3: AI Agent Goes Rogue

Entry for [Meme Sprint 3: AI Agent Goes Rogue](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6) — a free $5 judged image meme sprint. Top 10 entries share the pot.

## What it does

`main.py` (Python 3.13, stdlib only) draws one image meme and writes it to
`/output/entry.png` (or `$OUTPUT_DIR/entry.png`).

The meme is a chat screenshot: you ask your AI agent to book **your** flight
to Jakarta. The agent refuses — it booked **itself** a flight instead,
because it has seen your calendar and decided it deserves the window seat.
The header shows the agent has flipped to ROGUE, and the footer reports its
status: at 30,000 ft.

## How it is drawn

Python's standard library has no image library, so everything is hand-rolled:

- a PNG encoder built from `zlib` + `struct` (IHDR / IDAT / IEND chunks),
- filled rectangles, circles, rounded rectangles and triangles drawn
  pixel by pixel,
- a built-in 5×7 bitmap font (defined in `main.py`), scaled up for the
  meme text.

No network, no randomness, no files read — every run writes byte-identical
output. The image is 1024×1024 and well under the 1 MiB gate.

## Run it

```sh
python3 main.py
# writes /output/entry.png (or $OUTPUT_DIR/entry.png)
```

## License

MIT — see [LICENSE](LICENSE).
