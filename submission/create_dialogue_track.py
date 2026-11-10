"""Add a conversational, two-speaker English-India dialogue over the demo cut.

Layout goals:
- Each spoken line starts at (or near) the scene beat it describes.
- Clean narration only: no music or ambience noise under the speech.
- Dialogue finishes inside the video tail so nothing is clipped.
- Off-screen conversational voices are illustrative, separate from the app's
  Gnani Timbre feature. The speakers are not the people in the footage.
"""

from __future__ import annotations

import asyncio
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / ".video-deps"))
import edge_tts
import imageio_ffmpeg


ROOT = Path(__file__).parent
WORK = ROOT / ".render" / "story-cut" / "dialogue"
VIDEO_IN = ROOT / "Bank-Raasta-demo-final.mp4"
VIDEO_OUT = ROOT / "Bank-Raasta-demo.mp4"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

CUSTOMER = "en-IN-PrabhatNeural"
GUIDE = "en-IN-NeerjaExpressiveNeural"  # expressive Indian English, not the flat standard voice
CUSTOMER_RATE = 16   # % speaking-rate boost, per-line values may be raised to fit
GUIDE_RATE = 17
MODE = "sample mode"  # narrated state: no API key configured for this recording

# Visual cut table (mirrors submission/render_final_cut.py; 0.55 s cross dissolves).
SCENE_DURS = [4, 6, 5, 6, 7.5, 5, 12, 10, 12, 11, 13, 9, 12, 9, 11, 9]
XFADE = 0.55
VIDEO_END = 133.25   # nominal end of the visual cut
TAIL_LIMIT = 132.70  # narration must finish before this so nothing is clipped

# scene windows: (start, end) per rendered scene; each scene is visible from its
# start (the previous scene cross-dissolves out over the last XFADE seconds).
WINDOWS: list[tuple[float, float]] = []
_start = 0.0
for _i, _d in enumerate(SCENE_DURS):
    _end = _start + _d - (XFADE if _i else 0.0)
    WINDOWS.append((_start, _end))
    _start = _end
WINDOWS[-1] = (WINDOWS[-1][0], VIDEO_END)

# (speaker, text, scene index, lead-in seconds, latest acceptable end for this line)
# Scenes: 0 logo · 1 failed payment · 2 shop · 3 no reply · 4 RBI stat ·
# 5 bridge · 6 overview · 7 issue · 8 details · 9 Prisma · 10 next step ·
# 11 checklist · 12 summary · 13 privacy · 14 Timbre · 15 closing
DIALOGUE = [
    (GUIDE, "Bank Raasta. A guide for the moment a payment goes wrong.",
     0, 0.2, 5.6),
    (GUIDE, "The payment fails. Your money is debited.",
     1, 0.45, 9.0),
    (GUIDE, "The shop has no confirmation.",
     2, 0.45, 12.9),
    (GUIDE, "Twelve days. Still no reply.",
     3, 0.5, 18.8),
    (GUIDE, "In 2024-25, RBI received 13.34 lakh complaints.",
     4, 0.4, 25.8),
    (GUIDE, "Bank Raasta organizes the case and shows the possible next official step, without ever filing the complaint for you.",
     5, 0.35, 34.0),
    (GUIDE, "Here's the guide. Choose the issue, describe what happened, and see a suggested next step on one screen.",
     6, 0.0, 42.0),
    (GUIDE, "UPI, card, loan or EMI, or a bank service. Speech input supports ten languages.",
     7, 0.3, 51.2),
    (CUSTOMER, "What do I need to enter?",
     8, 0.35, 54.5),
    (GUIDE, "Date, bank or app, amount, what happened, the outcome you want, and whether you have complained.",
     8, 0.0, 62.0),
    (GUIDE, "Prefer speaking? Gnani Prisma turns speech into editable text. Review it before use. Sample mode; no API key.",
     9, 0.4, 72.9),
    (GUIDE, "The next-step guide follows your complaint dates and reply status, then links to RBI's official route.",
     10, 0.4, 84.0),
    (GUIDE, "A short checklist keeps the complaint number, bank reply, and transaction proof together.",
     11, 0.4, 93.3),
    (GUIDE, "Turn the case into a summary in Hindi or English. Copy it or download the text.",
     12, 0.4, 102.0),
    (CUSTOMER, "Do I share my PIN or OTP?",
     13, -3.2, 105.1),
    (GUIDE, "No. No bank login. Notes stay in this browser. Nothing is submitted for you.",
     13, 0.3, 113.3),
    (GUIDE, "For read-aloud, Gnani Timbre is wired for Hindi or English. Live speech needs a private key; this demo stays in sample mode.",
     14, 0.4, 123.8),
    (GUIDE, "Bank Raasta: a clearer next step when a bank complaint leaves you unsure.",
     15, 0.45, TAIL_LIMIT),
]

def base_rate(voice: str) -> int:
    return CUSTOMER_RATE if voice == CUSTOMER else GUIDE_RATE


# Deterministic per-line delivery nudges: consecutive lines no longer read at
# one flat rate and pitch, which is what made the narration sound robotic.
PITCH_CYCLE = ["+0Hz", "+3Hz", "-2Hz", "+1Hz"]
RATE_JITTER = (+2, -2, +1, -1)
TAGLINE = len(DIALOGUE) - 1


def line_pitch(index: int) -> str:
    if index == TAGLINE:
        return "+2Hz"  # closing line: slightly warmer lift
    return PITCH_CYCLE[index % len(PITCH_CYCLE)]


def line_rate(index: int, voice: str) -> int:
    if index == TAGLINE:
        return max(base_rate(voice) - 4, 0)  # closing line delivered slower
    return base_rate(voice) + RATE_JITTER[index % len(RATE_JITTER)]


def gap_for(index: int, prev_voice: str, voice: str) -> float:
    """Human-like breathing room between lines; it varies a little so the
    pauses do not fall on a metronome."""
    if prev_voice == voice:
        base = 0.18
    else:
        base = 0.30
    return base + (0.08 if index % 2 == 0 else 0.0)


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)


def media_duration(path: Path) -> float:
    result = run([FFMPEG, "-hide_banner", "-i", str(path)])
    match = re.search(r"Duration: (\d+):(\d+):(\d+\.?\d*)", result.stderr)
    if not match:
        raise RuntimeError(f"Could not read duration for {path}")
    return int(match.group(1)) * 3600 + int(match.group(2)) * 60 + float(match.group(3))


async def regenerate(index: int, voice: str, text: str, rate: int, pitch: str) -> Path:
    path = WORK / f"dialogue-{index + 1:02d}.mp3"
    await edge_tts.Communicate(
        text, voice=voice, rate=f"+{rate}%", pitch=pitch).save(str(path))
    return path


def layout(durations: list[float]) -> list[float]:
    """Sequential flow snapped to each line's scene beat."""
    starts: list[float] = []
    cursor = -1.0
    for index, (voice, _, scene, lead, _) in enumerate(DIALOGUE):
        target = WINDOWS[scene][0] + lead
        if index == 0:
            start = min(target, 0.4)
        else:
            start = max(cursor, target)
        starts.append(start)
        cursor = start + durations[index]
        if index < len(DIALOGUE) - 1:
            cursor += gap_for(index, voice, DIALOGUE[index + 1][0])
    return starts


def violations(durations: list[float], starts: list[float]) -> list[int]:
    bad: set[int] = set()
    for index, (_, _, _, _, limit) in enumerate(DIALOGUE):
        if starts[index] + durations[index] > limit:
            bad.add(index)
    if starts[-1] + durations[-1] > TAIL_LIMIT + 0.01:
        for later in range(len(DIALOGUE) - 2, max(9, len(DIALOGUE) - 6), -1):
            bad.add(later)
        bad.add(len(DIALOGUE) - 1)
    return sorted(bad)


async def build_clips() -> tuple[list[Path], list[float]]:
    WORK.mkdir(parents=True, exist_ok=True)
    for stale in sorted(WORK.glob("dialogue-*.mp3")):
        stale.unlink()
    rates = [line_rate(i, entry[0]) for i, entry in enumerate(DIALOGUE)]
    pitches = [line_pitch(i) for i in range(len(DIALOGUE))]
    clips: list[Path] = []
    durations: list[float] = []
    for attempt in range(1, 9):
        clips = await asyncio.gather(*[
            regenerate(i, voice, text, rate, pitch)
            for i, ((voice, text, *_), rate, pitch)
            in enumerate(zip(DIALOGUE, rates, pitches))
        ])
        durations = [media_duration(p) for p in clips]
        starts = layout(durations)
        bad = violations(durations, starts)
        if not bad:
            if attempt > 1:
                print(f"  (line pacing converged after {attempt} passes)")
            return clips, durations
        for i in bad:
            rates[i] = min(rates[i] + 4, 32)
        print(f"  pass {attempt}: adjusting pacing for lines "
              f"{', '.join(f'{i + 1:02d}' for i in bad)}")
    print("  warning: some lines may still overrun their beat")
    return clips, durations


def mix(clips: list[Path], durations: list[float]) -> None:
    starts = layout(durations)
    speech_end = starts[-1] + durations[-1]
    if speech_end > VIDEO_END - 0.4:
        raise RuntimeError(
            f"Narration ends at {speech_end:.1f}s, too close to the {VIDEO_END:.1f}s cut")

    command = [FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
               "-i", str(VIDEO_IN)]
    for clip in clips:
        command += ["-i", str(clip)]

    # Silent anchor keeps the mix as long as the video; the speech lines ride on
    # top of it. No music, no ambience: the narration stays cleanly audible.
    filters = ["[0:a]volume=0[dead]"]
    labels = ["dead"]
    for index, start in enumerate(starts, 1):
        delay_ms = round(start * 1000)
        label = f"v{index}"
        filters.append(f"[{index}:a]adelay={delay_ms}|{delay_ms},volume=1.15[{label}]")
        labels.append(label)
    inputs = "".join(f"[{label}]" for label in labels)
    filters.append(
        f"{inputs}amix=inputs={len(labels)}:duration=first:dropout_transition=0:normalize=0,"
        "alimiter=limit=0.93[aout]")
    command += ["-filter_complex", ";".join(filters),
                "-map", "0:v:0", "-map", "[aout]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-shortest", "-movflags", "+faststart", str(VIDEO_OUT)]
    run_result = subprocess.run(command)
    if run_result.returncode != 0:
        raise RuntimeError("final mix failed")

    scene_names = ["logo", "failed payment", "shop", "no reply", "RBI stat",
                   "bridge", "overview", "issue & language", "case details",
                   "Prisma voice", "next step", "checklist", "summary",
                   "privacy", "Timbre", "closing"]
    print(f"Created {VIDEO_OUT}")
    print(f"Narration segments: {len(DIALOGUE)} · speech ends {speech_end:.1f}s "
          f"of {VIDEO_END:.1f}s · clean narration, no background noise")
    for index, (start, (voice, text, scene, _, limit)) in enumerate(
            zip(starts, DIALOGUE)):
        marker = "" if start + durations[index] <= limit + 0.01 else "  (slight overrun)"
        print(f"  {index + 1:02d} {start:6.1f}s · {scene_names[scene]} · "
              f"{'Customer' if voice == CUSTOMER else 'Guide'}: {text[:52]}...{marker}")


def main() -> None:
    if not VIDEO_IN.exists():
        raise FileNotFoundError(f"Render the visual video first: {VIDEO_IN}")
    print("Generating voice clips...")
    clips, durations = asyncio.run(build_clips())
    mix(clips, durations)


if __name__ == "__main__":
    main()
