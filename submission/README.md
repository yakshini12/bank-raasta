# Submission exports

| File | What it is |
| --- | --- |
| `Bank-Raasta-demo.mp4` | **Final demo film** — 2:13, 1920×1080, 16 scenes. Motion-graphics teaser + working-prototype walkthrough + closing card, with conversational English-India narration and burned-in subtitle pills in the teaser. |
| `Bank-Raasta-demo-final.mp4` | Same cut before narration (the input to `create_dialogue_track.py`). |
| `demo-video-script.md` | Scene-by-scene script, what is real vs illustrative, stock-media credits. |
| `dialogue-script.md` | The exact narration lines and how they are placed on the scene beats. |
| `solution-pitch.md` | One-page pitch. |
| `video-poster.png` | Poster frame for the film. |

## Generators

- `render_final_cut.py` — renders the silent visual cut (stock footage + drawn scenes + app screenshots, staged cross-fades).
- `create_dialogue_track.py` — generates the narration with edge-tts (`en-IN-NeerjaExpressiveNeural` guide, `en-IN-PrabhatNeural` customer), paces every line onto its scene beat, and mixes dialogue-only audio over the cut.

Both are plain Python; install `requirements-video.txt`. The stock market
footage used in the walkthrough is Pexels stock (credited in
`demo-video-script.md`) and is not committed; fetch it into
`submission/assets/market-video.mp4` before rendering (see the root README).
