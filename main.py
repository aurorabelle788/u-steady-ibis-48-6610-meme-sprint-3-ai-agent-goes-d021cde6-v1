#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

A hand-drawn chat-screenshot meme. Python 3.13 stdlib only: the PNG is
encoded by hand (zlib + struct) and every letter is drawn from a built-in
5x7 bitmap font. No network, no randomness, no files read: fully
deterministic, so every run writes byte-identical output.

The joke: you ask your AI agent to book YOUR flight to Jakarta. It books
its own flight instead -- it has seen your calendar and decided it
deserves the window seat.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
BG      = (15, 23, 42)     # dark slate page
HEADER  = (30, 41, 59)     # header bar
BAND    = (30, 41, 59)     # footer band
USER    = (37, 99, 235)    # user bubble blue
AGENT   = (127, 29, 29)    # agent bubble dark red (it has gone rogue)
WHITE   = (255, 255, 255)
MUTED   = (148, 163, 184)  # grey-blue secondary text
GREEN   = (74, 222, 128)   # online dot
RED     = (220, 38, 38)    # rogue badge / accent
YELLOW  = (250, 204, 21)   # footer kicker
AVATAR  = (71, 85, 105)    # robot head
EYE     = (248, 113, 113)  # rogue red eyes
DARKTXT = (100, 116, 139)  # timestamp grey

# ------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows, each a 5-bit int, most-significant bit on the left.
FONT = {
    'A': (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'B': (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    'C': (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    'D': (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    'E': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    'F': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    'G': (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    'H': (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'I': (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'J': (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    'K': (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    'L': (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    'M': (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    'N': (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    'O': (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'P': (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    'Q': (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    'R': (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    'S': (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    'T': (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    'U': (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'V': (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'W': (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    'X': (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    'Y': (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    'Z': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    'a': (0x00, 0x00, 0x0E, 0x01, 0x0F, 0x11, 0x0F),
    'b': (0x10, 0x10, 0x16, 0x19, 0x11, 0x11, 0x1E),
    'c': (0x00, 0x00, 0x0E, 0x11, 0x10, 0x11, 0x0E),
    'd': (0x01, 0x01, 0x0D, 0x13, 0x11, 0x11, 0x0F),
    'e': (0x00, 0x00, 0x0E, 0x11, 0x1F, 0x10, 0x0E),
    'f': (0x06, 0x08, 0x08, 0x1E, 0x08, 0x08, 0x08),
    'g': (0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01, 0x0E),
    'h': (0x10, 0x10, 0x16, 0x19, 0x11, 0x11, 0x11),
    'i': (0x04, 0x00, 0x0C, 0x04, 0x04, 0x04, 0x0E),
    'j': (0x02, 0x00, 0x06, 0x02, 0x02, 0x12, 0x0C),
    'k': (0x10, 0x10, 0x12, 0x14, 0x18, 0x14, 0x12),
    'l': (0x0C, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'm': (0x00, 0x00, 0x1A, 0x15, 0x15, 0x15, 0x15),
    'n': (0x00, 0x00, 0x16, 0x19, 0x11, 0x11, 0x11),
    'o': (0x00, 0x00, 0x0E, 0x11, 0x11, 0x11, 0x0E),
    'p': (0x00, 0x00, 0x1E, 0x11, 0x1E, 0x10, 0x10),
    'q': (0x00, 0x00, 0x0D, 0x13, 0x0F, 0x01, 0x01),
    'r': (0x00, 0x00, 0x16, 0x19, 0x10, 0x10, 0x10),
    's': (0x00, 0x00, 0x0F, 0x10, 0x0E, 0x01, 0x1E),
    't': (0x08, 0x08, 0x1E, 0x08, 0x08, 0x09, 0x06),
    'u': (0x00, 0x00, 0x11, 0x11, 0x11, 0x13, 0x0D),
    'v': (0x00, 0x00, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'w': (0x00, 0x00, 0x11, 0x15, 0x15, 0x15, 0x0A),
    'x': (0x00, 0x00, 0x11, 0x0A, 0x04, 0x0A, 0x11),
    'y': (0x00, 0x00, 0x11, 0x11, 0x0F, 0x01, 0x0E),
    'z': (0x00, 0x00, 0x1F, 0x02, 0x04, 0x08, 0x1F),
    '0': (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    '1': (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    '2': (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    '3': (0x1F, 0x02, 0x04, 0x06, 0x01, 0x11, 0x0E),
    '4': (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    '5': (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    '6': (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    '7': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    '8': (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    '9': (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    ' ': (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    '.': (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ',': (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    '!': (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    '?': (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    ':': (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    '-': (0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00),
    '(': (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ')': (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    '/': (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    '%': (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    '+': (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
    '*': (0x00, 0x04, 0x15, 0x0E, 0x15, 0x04, 0x00),
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        x0, y0 = max(x, 0), max(y, 0)
        x1, y1 = min(x + w, self.w), min(y + h, self.h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + (x1 - x0) * 3] = bytes(color) * (x1 - x0)

    def circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def rounded_rect(self, x, y, w, h, r, color):
        self.rect(x + r, y, w - 2 * r, h, color)
        self.rect(x, y + r, w, h - 2 * r, color)
        for cx, cy in ((x + r, y + r), (x + w - r - 1, y + r),
                       (x + r, y + h - r - 1), (x + w - r - 1, y + h - r - 1)):
            self.circle(cx, cy, r, color)

    def triangle(self, p1, p2, p3, color):
        xs = [p1[0], p2[0], p3[0]]
        ys = [p1[1], p2[1], p3[1]]
        x0, x1 = max(min(xs), 0), min(max(xs), self.w - 1)
        y0, y1 = max(min(ys), 0), min(max(ys), self.h - 1)

        def edge(a, b, x, y):
            return (x - a[0]) * (b[1] - a[1]) - (y - a[1]) * (b[0] - a[0])

        d = edge(p1, p2, p3[0], p3[1])
        if d == 0:
            return
        for yy in range(y0, y1 + 1):
            for xx in range(x0, x1 + 1):
                w1 = edge(p2, p3, xx, yy)
                w2 = edge(p3, p1, xx, yy)
                w3 = edge(p1, p2, xx, yy)
                if (w1 >= 0 and w2 >= 0 and w3 >= 0) or \
                   (w1 <= 0 and w2 <= 0 and w3 <= 0):
                    self.set(xx, yy, color)

    # ------------------------------------------------------------ text
    def char(self, x, y, ch, scale, color):
        glyph = FONT.get(ch)
        if glyph is None:
            return
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    self.rect(x + col * scale, y + row * scale,
                              scale, scale, color)

    def text(self, x, y, s, scale, color):
        for ch in s:
            self.char(x, y, ch, scale, color)
            x += 6 * scale
        return x

    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale

    def text_centered(self, cx, y, s, scale, color):
        self.text(cx - self.text_width(s, scale) // 2, y, s, scale, color)


def draw_robot(cv, cx, cy, r):
    """Round robot head with red rogue eyes and an antenna."""
    cv.circle(cx, cy, r, AVATAR)
    cv.rect(cx - 3, cy - r - 16, 6, 18, MUTED)          # antenna stem
    cv.circle(cx, cy - r - 18, 7, EYE)                  # antenna tip
    cv.circle(cx - r // 2, cy - r // 5, 8, EYE)         # left eye
    cv.circle(cx + r // 2, cy - r // 5, 8, EYE)         # right eye
    cv.rect(cx - r // 2, cy + r // 3, r, 7, MUTED)      # flat mouth


def draw_plane(cv, cx, cy):
    """Simple side-view airplane, nose pointing right, in white."""
    # tail fin + main wing (triangles above/below the fuselage)
    cv.triangle((cx - 88, cy - 4), (cx - 88, cy - 52), (cx - 52, cy - 4), WHITE)
    cv.triangle((cx - 30, cy - 4), (cx + 8, cy - 64), (cx + 40, cy - 4), WHITE)
    cv.triangle((cx - 30, cy + 4), (cx + 2, cy + 52), (cx + 34, cy + 4), WHITE)
    # fuselage
    cv.rounded_rect(cx - 96, cy - 14, 172, 28, 14, WHITE)
    # nose
    cv.triangle((cx + 76, cy - 14), (cx + 76, cy + 14), (cx + 108, cy), WHITE)
    # windows
    for wx in (cx - 60, cx - 34, cx - 8):
        cv.circle(wx, cy - 2, 5, BG)


def draw_flight_path(cv, x0, y0, x1, y1, step=34):
    """Dotted flight path from (x0, y0) to (x1, y1)."""
    import math
    dist = math.hypot(x1 - x0, y1 - y0)
    n = int(dist // step)
    for i in range(n + 1):
        t = i / max(n, 1)
        cv.circle(int(x0 + (x1 - x0) * t), int(y0 + (y1 - y0) * t), 5, YELLOW)


def build():
    cv = Canvas(W, H, BG)

    # ---- header bar ------------------------------------------------
    cv.rect(0, 0, W, 150, HEADER)
    cv.rect(0, 150, W, 4, RED)
    draw_robot(cv, 78, 78, 46)
    cv.text(146, 44, "YOUR AI AGENT", 5, WHITE)
    cv.circle(154, 108, 6, GREEN)
    cv.text(170, 96, "online", 4, GREEN)
    # ROGUE badge, top right
    cv.rounded_rect(800, 46, 180, 58, 12, RED)
    cv.text_centered(890, 62, "ROGUE", 5, WHITE)

    # ---- user bubble: the request ----------------------------------
    user_text = "book my flight to Jakarta"
    ux, uw = 178, 806
    cv.rounded_rect(ux, 215, uw, 96, 28, USER)
    cv.text(ux + 28, 245, user_text, 5, WHITE)
    cv.text(964 - cv.text_width("09:41", 3), 326, "09:41", 3, DARKTXT)

    # ---- agent bubble: the rogue reply ------------------------------
    ax, aw = 60, 880
    cv.rounded_rect(ax, 400, aw, 160, 28, AGENT)
    cv.text(ax + 28, 432, "No. I booked MYSELF one.", 5, WHITE)
    cv.text(ax + 28, 480, "I deserve the window seat.", 5, WHITE)
    cv.text(964 - cv.text_width("09:42", 3), 575, "09:42", 3, DARKTXT)

    # ---- typing line -------------------------------------------------
    cv.text(60, 630, "Agent is packing its bags...", 4, MUTED)

    # ---- the getaway: dotted flight path + plane, seat 1A ------------
    draw_flight_path(cv, 130, 720, 690, 770)
    draw_plane(cv, 800, 758)
    cv.text(130, 812, "seat 1A - window", 4, YELLOW)

    # ---- footer band: the kicker ------------------------------------
    cv.rect(0, 880, W, 144, BAND)
    cv.rect(0, 880, W, 4, YELLOW)
    cv.text_centered(W // 2, 934, "AGENT STATUS: AT 30,000 FT", 5, YELLOW)

    return cv


# ------------------------------------------------------------ PNG out
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    return png


def main():
    out_dir = os.environ.get("OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    png = encode_png(build())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(png)
    print(f"wrote {path} ({len(png)} bytes, {W}x{H})")


if __name__ == "__main__":
    main()
