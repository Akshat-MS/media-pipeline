# res/library/icons/

Brand assets. **Tracked in git** — `.gitignore` covers only `res/inputs`,
`res/outputs` and `res/workdir`, and the media rules cover video and audio.
These must survive a fresh clone, so they belong here rather than in `res/workdir`.

| File | What it is | Use |
|---|---|---|
| `eklakshya.jpeg` | the original as supplied, 512×183 | provenance — never rendered from |
| `eklakshya-trim.png` | trimmed to content, 497×164, keeps its `#F7F7F7` ground | a plate matched to `#F7F7F7` |
| **`eklakshya-alpha.png`** | ground keyed out, edge colours un-multiplied | **current: any plate colour, including pure white** |
| `eklakshya-knockout.png` | wordmark and rule recoloured white, artwork kept | no plate — mark sits directly on the slide |

## Measured, from the original

| | |
|---|---|
| ground colour | `#F7F7F7` — 52% of pixels, **not pure white** |
| wordmark colour | `#000327` |
| wordmark on its own ground | 18.81:1 |
| wordmark on navy `#16234A` | **1.32:1 — invisible** |
| wordmark on blue `#0B2E5C` | 1.50:1 |
| wordmark on green `#26301C` | 1.46:1 |
| aspect ratio, trimmed | 3.03:1 |

The 1.32:1 figure is why a plate or a knockout is required, and why the mark can
never sit bare on a dark slide in its supplied form.

## Provenance and its limit

`-trim` is a lossless crop. `-alpha` and `-knockout` are **derived by threshold from
a JPEG** — a script decided which pixels were the ground and which were the wordmark.
That is a computation standing in for a judgement, and on a logo it is the kind of
approximation a brand owner notices before anyone else does.

**If a vector original (`.ai`, `.eps`, `.svg`) or an official white-on-dark variant
exists, it replaces both derived files.** Ask before relying on them for anything
printed or client-facing.
