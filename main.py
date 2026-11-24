#!/usr/bin/env python3
"""THE WORLD IN ONE DAY - Tuesday 24 November 2026.

A pure Python 3 standard-library program that deterministically draws a
newspaper front page and writes a single 1024x1024 entry.png.

Everything is built from scratch in this file:
  * a raster canvas (a list of rows of RGB tuples),
  * a 5x7 bitmap font for A-Z, 0-9 and basic punctuation,
  * drawing helpers (rectangles, lines, circles, scaled text),
  * small motif illustrations drawn per story panel,
  * a PNG encoder built on zlib + struct.

No PIL, no network, no external assets, no randomness, no timestamps:
two runs always produce byte-identical output.
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
PAPER = (246, 242, 233)
INK = (22, 22, 26)
RED = (178, 34, 34)
BLUE = (28, 74, 140)
SKY = (168, 205, 232)
SEA = (36, 110, 160)
GREY = (110, 110, 110)
LIGHT = (226, 220, 205)
GOLD = (196, 150, 40)
GREEN = (34, 120, 70)
ORANGE = (214, 110, 30)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# ---------------------------------------------------------------- canvas
CANVAS = [[PAPER for _ in range(W)] for _ in range(H)]


def set_px(x, y, colour):
    if 0 <= x < W and 0 <= y < H:
        CANVAS[y][x] = colour


def rect(x, y, w, h, colour):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            set_px(xx, yy, colour)


def frame(x, y, w, h, colour, thick=2):
    rect(x, y, w, thick, colour)
    rect(x, y + h - thick, w, thick, colour)
    rect(x, y, thick, h, colour)
    rect(x + w - thick, y, thick, h, colour)


def hline(x, y, w, colour, thick=1):
    rect(x, y, w, thick, colour)


def vline(x, y, h, colour, thick=1):
    rect(x, y, thick, h, colour)


def line(x0, y0, x1, y1, colour, thick=1):
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(steps + 1):
        x = x0 + (x1 - x0) * i // steps
        y = y0 + (y1 - y0) * i // steps
        rect(x, y, thick, thick, colour)


def circle(cx, cy, r, colour, fill=False):
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            d2 = dx * dx + dy * dy
            if fill and d2 <= r * r:
                set_px(cx + dx, cy + dy, colour)
            elif not fill and r * r - 2 * r <= d2 <= r * r:
                set_px(cx + dx, cy + dy, colour)


def triangle(x, y, size, colour):
    for row in range(size):
        rect(x + row // 2, y + row, size - row, 1, colour)

# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 pixels, encoded as strings of '1' and '0'.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "01010", "00100", "00100", "00100", "01010", "10001"),
    "Y": ("10001", "01010", "00100", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(x, y, text, scale, colour=INK):
    cx = x
    for ch in text.upper():
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    rect(cx + col * scale, y + row * scale, scale, scale, colour)
        cx += 6 * scale
    return cx


def draw_centered(y, text, scale, colour=INK):
    x = (W - text_width(text, scale)) // 2
    draw_text(x, y, text, scale, colour)


def wrap(text, max_chars):
    words = text.upper().split()
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if len(trial) <= max_chars:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_block(x, y, text, scale, colour, max_chars, leading=3):
    lines = wrap(text, max_chars)
    for i, ln in enumerate(lines):
        draw_text(x, y + i * (7 * scale + leading), ln, scale, colour)
    return y + len(lines) * (7 * scale + leading)

# ---------------------------------------------------------------- motifs
def draw_ship(x, y):
    """Lead illustration: a warship on waves, drones overhead, a splash."""
    rect(x, y, 300, 92, SKY)
    circle(x + 262, y + 16, 11, GOLD, fill=True)
    # naval drones in the sky
    for dx, dy in ((18, 12), (52, 22), (86, 10)):
        rect(x + dx, y + dy, 16, 4, INK)
        rect(x + dx + 6, y + dy - 3, 4, 10, INK)
    rect(x, y + 58, 300, 34, SEA)
    for wx in range(0, 300, 24):  # wave crests
        rect(x + wx, y + 62, 12, 3, WHITE)
        rect(x + (wx + 12) % 300, y + 76, 12, 3, SKY)
    # hull, deck, bridge and mast of the corvette
    rect(x + 78, y + 46, 150, 14, (70, 74, 82))
    triangle(x + 210, y + 46, 14, (70, 74, 82))
    rect(x + 118, y + 34, 52, 12, (96, 100, 110))
    rect(x + 134, y + 20, 8, 14, INK)
    rect(x + 104, y + 28, 26, 4, INK)
    # splash where a drone struck
    for sx, sy in ((238, 40), (246, 32), (254, 42), (242, 48)):
        circle(x + sx, y + sy, 3, WHITE, fill=True)
    rect(x + 240, y + 44, 4, 16, ORANGE)


def draw_chip(x, y):
    rect(x, y, 44, 44, GREEN)
    rect(x + 10, y + 10, 24, 24, GOLD)
    for i in range(4):
        vline(x - 6, y + 6 + i * 10, 6, INK, 3)
        vline(x + 47, y + 6 + i * 10, 6, INK, 3)
        hline(x + 6 + i * 10, y - 6, 3, INK)
        hline(x + 6 + i * 10, y + 47, 3, INK)


def draw_satellite(x, y):
    circle(x + 22, y + 20, 9, INK, fill=True)
    rect(x + 32, y + 8, 18, 10, BLUE)
    rect(x - 6, y + 26, 18, 10, BLUE)
    line(x + 30, y + 30, x + 44, y + 44, RED, 2)
    line(x + 36, y + 28, x + 48, y + 40, RED, 2)


def draw_scales(x, y):
    vline(x + 20, y, 40, GOLD, 3)
    hline(x + 2, y + 2, 40, GOLD, 3)
    line(x + 4, y + 4, x - 2, y + 22, GOLD, 2)
    line(x + 4, y + 4, x + 10, y + 22, GOLD, 2)
    rect(x - 4, y + 22, 16, 4, GOLD)
    line(x + 38, y + 4, x + 32, y + 22, GOLD, 2)
    line(x + 38, y + 4, x + 44, y + 22, GOLD, 2)
    rect(x + 30, y + 22, 16, 4, GOLD)
    hline(x + 8, y + 42, 28, GOLD, 3)


def draw_cloud_sun(x, y):
    circle(x + 14, y + 12, 9, ORANGE, fill=True)
    rect(x + 2, y + 20, 42, 12, GREY)
    circle(x + 12, y + 22, 8, GREY, fill=True)
    circle(x + 30, y + 22, 9, GREY, fill=True)
    line(x + 10, y + 36, x + 6, y + 44, BLUE, 2)
    line(x + 24, y + 36, x + 20, y + 44, BLUE, 2)
    line(x + 36, y + 36, x + 32, y + 44, BLUE, 2)


def draw_cross(x, y):
    rect(x + 4, y + 4, 36, 36, WHITE)
    frame(x + 4, y + 4, 36, 36, RED, 2)
    rect(x + 18, y + 12, 8, 20, RED)
    rect(x + 12, y + 18, 20, 8, RED)


def draw_spots(x, y):
    circle(x + 22, y + 22, 18, (240, 200, 200), fill=False)
    for dx, dy in ((14, 14), (28, 18), (20, 28), (32, 30), (12, 30)):
        circle(x + dx, y + dy, 3, RED, fill=True)


MOTIFS = {
    "CHIP": draw_chip,
    "SAT": draw_satellite,
    "SCALES": draw_scales,
    "CLOUD": draw_cloud_sun,
    "CROSS": draw_cross,
    "SPOTS": draw_spots,
}

# ---------------------------------------------------------------- stories
# Researched from world-news reporting dated Tuesday 24 November 2026.
LEAD_HEADLINE = "UKRAINE SAYS IT SANK RUSSIAN WARSHIP OFF LIBYA"
LEAD_SUMMARY = (
    "PRESIDENT ZELENSKY SAID SEVEN NAVAL DRONES SANK THE RUSSIAN CORVETTE "
    "MERKURY AT BENGHAZI PORT. THE UN URGED AN INDEPENDENT PROBE INTO THE "
    "BENGHAZI PORT ATTACKS, AND TRIPOLI DEMANDED ANSWERS FROM KYIV."
)

PANELS = [
    ("CHIP", "NVIDIA REINSTATES HUANG AS CEO",
     "FOUNDER JENSEN HUANG RETURNED AS NVIDIA CHIEF AFTER TRUMP "
     "PRESSURE. SHARES SURGED, NASDAQ UP 6.51 PERCENT."),
    ("SAT", "NATO VOWS TO DEFEND SPACE",
     "NATO CHIEF MARK RUTTE VOWED TO DEFEND AGAINST SPACE THREATS "
     "AMID REPORTS OF A RUSSIAN NUCLEAR SATELLITE."),
    ("SCALES", "ICJ: MYANMAR GENOCIDE RULING",
     "THE WORLD COURT FOUND MYANMAR COMMITTED GENOCIDE AGAINST THE "
     "ROHINGYA. FOURTEEN COUNTRIES BACKED THE RULING."),
    ("CLOUD", "COP31 CLIMATE TALKS FAIL",
     "THE UN CLIMATE SUMMIT ENDED WITHOUT A DEAL AFTER SPLITS OVER "
     "FOSSIL FUELS AND CLIMATE FINANCE."),
    ("CROSS", "CONGO FIGHTING TRAPS EBOLA",
     "HEAVY FIGHTING NEAR A HOSPITAL IN ITURI FORCED WHO EBOLA "
     "RESPONDERS TO TAKE COVER FOR OVER 24 HOURS."),
    ("SPOTS", "US LOSES MEASLES-FREE STATUS",
     "PENNSYLVANIA RECORDED A NINTH MEASLES DEATH IN AN OUTBREAK "
     "ACROSS 46 COUNTIES, ENDING US ELIMINATION."),
]


def panel(x, y, w, h, motif, headline, summary):
    frame(x, y, w, h, INK, 2)
    MOTIFS[motif](x + 14, y + 16)
    tx = x + 72
    draw_block(tx, y + 12, headline, 2, RED, 30)
    draw_block(tx, y + 48, summary, 2, INK, 30)


def build_page():
    rect(0, 0, W, H, PAPER)
    frame(14, 14, W - 28, H - 28, INK, 3)
    # masthead
    draw_centered(34, "THE WORLD IN ONE DAY", 7, INK)
    hline(48, 96, W - 96, INK, 3)
    draw_centered(106, "TUESDAY 24 NOVEMBER 2026", 3, RED)
    draw_text(48, 108, "ONE IMAGE", 2, GREY)
    draw_text(W - 48 - text_width("EST. 2026", 2), 108, "EST. 2026", 2, GREY)
    hline(48, 138, W - 96, INK, 1)
    # lead story
    draw_text(48, 152, "LEAD STORY - BENGHAZI, LIBYA", 2, BLUE)
    y = 176
    for ln in wrap(LEAD_HEADLINE, 21):
        draw_text(48, y, ln, 5, INK)
        y += 42
    draw_ship(48, y + 6)
    draw_block(372, y + 6, LEAD_SUMMARY, 2, INK, 46)
    draw_block(372, y + 94, "ALSO: GERMANY FIRST TO ACCESS UKRAINE "
               "DELTA SYSTEM. GAZA STRIKES KILL SIX.", 2, GREY, 46)
    lead_bottom = y + 140
    hline(48, lead_bottom + 10, W - 96, INK, 2)
    # six secondary panels, two columns by three rows
    px = [48, 524]
    pw = 452
    ph = 148
    top = lead_bottom + 24
    for i, (motif, headline, summary) in enumerate(PANELS):
        col = i % 2
        row = i // 2
        panel(px[col], top + row * (ph + 14), pw, ph, motif, headline, summary)
    footer_y = top + 3 * (ph + 14) + 2
    hline(48, footer_y, W - 96, INK, 1)
    draw_centered(footer_y + 10, "ALL HEADLINES REPORTED TUESDAY 24 NOVEMBER 2026", 2, GREY)


# ---------------------------------------------------------------- PNG out
def encode_png():
    raw = bytearray()
    for row in CANVAS:
        raw.append(0)  # filter type 0 for every scanline
        for (r, g, b) in row:
            raw.extend((r, g, b))
    compressed = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", compressed)
    png += chunk(b"IEND", b"")
    return png


def main():
    build_page()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(encode_png())
    print("wrote", path)


if __name__ == "__main__":
    main()
