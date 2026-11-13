#!/usr/bin/env python3
"""Generate the Kiro 98 pack's original art and sounds.

Writes branding/*.svg, loader/hourglass.svg and audio/*.wav from code, so every
asset in the pack is original (no third-party icons or sounds). Stdlib only.

    python3 .github/scripts/build_assets.py
"""

from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# ── palette ──
K = "#0a0a0a"  # outline
W = "#ffffff"
SILVER = "#c0c0c0"
LIGHT = "#dfdfdf"
SHADOW = "#808080"
NAVY = "#000080"
BLUE = "#1084d0"
TEAL = "#008080"
SAND = "#d89a00"

GHOST = [
    "....KKKKKK....",
    "..KKWWWWWWKK..",
    ".KWWWWWWWWWWK.",
    ".KWWWWWWWWWWK.",
    "KWWWEEWWEEWWWK",
    "KWWWEEWWEEWWWK",
    "KWWWWWWWWWWWWK",
    "KWWWWWWWWWWWWK",
    "KWWWWWWWWWWWWK",
    "KWWWWWWWWWWWWK",
    "KWWWWWWWWWWWWK",
    "KWWWWWWWWWWWWK",
    "KWWKKWWWWKKWWK",
    "KWK..KWWK..KWK",
    "KK....KK....KK",
]

MINI_GHOST = [
    "..KKKK..",
    ".KWWWWK.",
    "KWEWWEWK",
    "KWWWWWWK",
    "KWWWWWWK",
    "KWWWWWWK",
    "KWKWWKWK",
    "KK.KK.KK",
]

GHOST_COLORS = {"K": K, "W": W, "E": K}


def sprite_rects(rows: list[str], colors: dict[str, str], x0: float = 0, y0: float = 0, px: float = 1) -> str:
    """Pixel rows -> <rect>s, merging horizontal runs of the same color."""
    out = []
    for y, row in enumerate(rows):
        x = 0
        while x < len(row):
            ch = row[x]
            if ch not in colors:
                x += 1
                continue
            run = 1
            while x + run < len(row) and row[x + run] == ch:
                run += 1
            out.append(
                f'<rect x="{x0 + x * px:g}" y="{y0 + y * px:g}" width="{run * px:g}" '
                f'height="{px:g}" fill="{colors[ch]}"/>'
            )
            x += run
    return "".join(out)


def bevel(x: int, y: int, w: int, h: int, face: str = SILVER, raised: bool = True) -> str:
    """A Win9x-style 2px bevelled box, in whole pixels."""
    hi, lo = (W, K) if raised else (SHADOW, W)
    hi2, lo2 = (LIGHT, SHADOW) if raised else (K, LIGHT)
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{lo}"/>'
        f'<rect x="{x}" y="{y}" width="{w - 1}" height="{h - 1}" fill="{hi}"/>'
        f'<rect x="{x + 1}" y="{y + 1}" width="{w - 2}" height="{h - 2}" fill="{lo2}"/>'
        f'<rect x="{x + 1}" y="{y + 1}" width="{w - 3}" height="{h - 3}" fill="{hi2}"/>'
        f'<rect x="{x + 2}" y="{y + 2}" width="{w - 4}" height="{h - 4}" fill="{face}"/>'
    )


def svg(view_w: float, view_h: float, body: str, extra: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_w:g} {view_h:g}" '
        f'shape-rendering="crispEdges"{extra}>{body}</svg>\n'
    )


def logo() -> str:
    # 16x16: the ghost alone reads best at command-palette size.
    return svg(16, 16, sprite_rects(GHOST, GHOST_COLORS, 1, 0.5))


def favicon() -> str:
    body = f'<rect width="16" height="16" fill="{TEAL}"/>' + sprite_rects(GHOST, GHOST_COLORS, 1, 0.5)
    return svg(16, 16, body)


def welcome() -> str:
    # 24x24 grid -> 2px per pixel in the 48px hero slot: a monitor showing the ghost.
    body = bevel(1, 1, 22, 16)  # bezel
    body += f'<rect x="3" y="3" width="18" height="12" fill="{SHADOW}"/>'
    body += f'<rect x="4" y="4" width="17" height="11" fill="{K}"/>'
    body += f'<rect x="4" y="4" width="16" height="10" fill="{TEAL}"/>'
    body += sprite_rects(MINI_GHOST, GHOST_COLORS, 8, 5)
    body += '<rect x="19" y="15" width="1" height="1" fill="#00c000"/>'  # power LED
    body += f'<rect x="9" y="17" width="6" height="2" fill="{SHADOW}"/>'  # neck
    body += bevel(4, 19, 16, 4)  # base
    return svg(24, 24, body)


def splash() -> str:
    # Desktop boot splash, drawn over the theme accent.
    ghost = sprite_rects(GHOST, GHOST_COLORS, 40, 75, 8)
    blocks = "".join(
        f'<rect x="{184 + i * 18}" y="196" width="14" height="14" fill="{NAVY}">'
        f'<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{i / 14:.3f};{min(1, i / 14 + 0.001):.3f};1" '
        f'dur="2.8s" repeatCount="indefinite"/></rect>'
        for i in range(14)
    )
    body = (
        f'<rect x="176" y="188" width="264" height="30" fill="{W}"/>'
        f'<rect x="176" y="188" width="263" height="29" fill="{SHADOW}"/>'
        f'<rect x="178" y="190" width="260" height="26" fill="{SILVER}"/>'
        + blocks
        + ghost
        + '<text x="176" y="140" font-family="Arial Black, Helvetica, sans-serif" '
        f'font-weight="900" font-size="64" fill="{W}">Kiro</text>'
        '<text x="342" y="140" font-family="Arial Black, Helvetica, sans-serif" '
        'font-weight="900" font-size="64" fill="#ffb000">98</text>'
        '<text x="178" y="172" font-family="Helvetica, Arial, sans-serif" font-size="18" '
        f'fill="{W}">Starting Kiro 98…</text>'
    )
    return svg(480, 270, body, ' preserveAspectRatio="xMidYMid meet"').replace(
        'shape-rendering="crispEdges"', 'shape-rendering="crispEdges" text-rendering="geometricPrecision"'
    )


def hourglass() -> str:
    # Animated loader: sand drains for 80% of the beat, then the glass flips.
    dur = "2.4s"
    glass = "3,2 13,2 8.6,8 13,14 3,14 7.4,8"
    top_tri = "3.8,2.6 12.2,2.6 8,7.6"
    bot_tri = "8,8.4 12.2,13.4 3.8,13.4"
    body = (
        '<defs>'
        f'<clipPath id="t"><polygon points="{top_tri}"/></clipPath>'
        f'<clipPath id="b"><polygon points="{bot_tri}"/></clipPath>'
        '</defs>'
        '<g>'
        '<animateTransform attributeName="transform" type="rotate" '
        f'values="0 8 8;0 8 8;180 8 8" keyTimes="0;0.8;1" dur="{dur}" repeatCount="indefinite"/>'
        f'<polygon points="{glass}" fill="{W}" stroke="{K}" stroke-width="0.8" stroke-linejoin="miter"/>'
        f'<rect x="3" y="2.6" width="10" height="5.2" fill="{SAND}" clip-path="url(#t)">'
        f'<animate attributeName="y" values="2.6;7.6;7.6" keyTimes="0;0.8;1" dur="{dur}" repeatCount="indefinite"/>'
        '</rect>'
        f'<rect x="3" y="13.4" width="10" height="5.2" fill="{SAND}" clip-path="url(#b)">'
        f'<animate attributeName="y" values="13.4;8.4;8.4" keyTimes="0;0.8;1" dur="{dur}" repeatCount="indefinite"/>'
        '</rect>'
        f'<rect x="7.7" y="7.6" width="0.6" height="5.8" fill="{SAND}">'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.78;0.8;1" dur="{dur}" repeatCount="indefinite"/>'
        '</rect>'
        f'<rect x="2" y="0.8" width="12" height="1.6" fill="{NAVY}" stroke="{K}" stroke-width="0.4"/>'
        f'<rect x="2" y="13.6" width="12" height="1.6" fill="{NAVY}" stroke="{K}" stroke-width="0.4"/>'
        '</g>'
    )
    return svg(16, 16, body).replace(' shape-rendering="crispEdges"', "")


# ── sounds (original synthesis, 22.05 kHz mono 16-bit) ──
RATE = 22050


def _write_wav(path: Path, samples: list[float]) -> None:
    peak = max(1e-9, max(abs(s) for s in samples))
    scale = 0.7 / peak
    frames = b"".join(struct.pack("<h", int(max(-1, min(1, s * scale)) * 32767)) for s in samples)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(frames)


def _tone(freq: float, start: float, length: float, total: float, decay: float, partials=((1, 1.0), (2, 0.25), (3, 0.08))) -> list[float]:
    n = int(total * RATE)
    out = [0.0] * n
    s0 = int(start * RATE)
    for i in range(int(length * RATE)):
        j = s0 + i
        if j >= n:
            break
        t = i / RATE
        env = min(1.0, t / 0.015) * math.exp(-t / decay)
        out[j] += env * sum(a * math.sin(2 * math.pi * freq * m * t) for m, a in partials)
    return out


def _mix(*tracks: list[float]) -> list[float]:
    n = max(len(t) for t in tracks)
    return [sum(t[i] for t in tracks if i < len(t)) for i in range(n)]


def startup_chime() -> list[float]:
    total = 4.0
    notes = [311.13, 392.00, 466.16, 587.33, 698.46, 932.33]  # Eb G Bb D F Bb
    tracks = [_tone(f, 0.16 * k, total - 0.16 * k, total, 1.1 + 0.15 * k) for k, f in enumerate(notes)]
    pad = _tone(155.56, 0.0, total, total, 2.2, ((1, 0.5), (2, 0.2)))
    mixed = _mix(*tracks, pad)
    fade = int(0.4 * RATE)
    for i in range(fade):
        mixed[-1 - i] *= i / fade
    return mixed


def ding() -> list[float]:
    total = 0.8
    return _mix(_tone(1046.5, 0, total, total, 0.22, ((1, 1.0), (2.76, 0.18))), _tone(1568.0, 0.06, total, total, 0.18))


def error_bonk() -> list[float]:
    total = 0.55
    n = int(total * RATE)
    out = []
    for i in range(n):
        t = i / RATE
        f = 233.08 * (1 - 0.18 * t / total)
        env = min(1.0, t / 0.008) * math.exp(-t / 0.16)
        out.append(env * (math.sin(2 * math.pi * f * t) + 0.3 * math.sin(2 * math.pi * 2 * f * t)))
    return out


def main() -> None:
    (ROOT / "branding").mkdir(exist_ok=True)
    (ROOT / "loader").mkdir(exist_ok=True)
    (ROOT / "audio").mkdir(exist_ok=True)
    (ROOT / "branding" / "logo.svg").write_text(logo())
    (ROOT / "branding" / "favicon.svg").write_text(favicon())
    (ROOT / "branding" / "welcome.svg").write_text(welcome())
    # Kiro Crew 0.12.2 rejects branding/splash.svg; newer builds accept it.
    # Kept outside the pack until then: move it to branding/ to enable.
    (ROOT / ".github" / "art").mkdir(parents=True, exist_ok=True)
    (ROOT / ".github" / "art" / "splash.svg").write_text(splash())
    (ROOT / "loader" / "hourglass.svg").write_text(hourglass())
    _write_wav(ROOT / "audio" / "startup.wav", startup_chime())
    _write_wav(ROOT / "audio" / "ding.wav", ding())
    _write_wav(ROOT / "audio" / "error.wav", error_bonk())
    for p in sorted([*ROOT.glob("branding/*"), *ROOT.glob("loader/*"), *ROOT.glob("audio/*.wav")]):
        print(f"{p.relative_to(ROOT)}  {p.stat().st_size} bytes")


if __name__ == "__main__":
    main()
