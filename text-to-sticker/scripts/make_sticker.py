#!/usr/bin/env python3
"""
WhatsApp Sticker Generator — Sweet Quote Style
Text → .webp with auto mood-based color theming

Usage:
    python3 make_sticker.py --text "Teks kamu" [options]
    python3 make_sticker.py --text "Teks kamu" --style sweet --bg-color "#FF6B6B"
"""

import argparse
import textwrap
import os
import sys
import re

from PIL import Image, ImageDraw, ImageFont


# ── Mood → Color Palette ──────────────────────────────────────────────────────

MOOD_PALETTES = {
    # Nama mood → (bg_color, accent/text_color, quote_color)
    # Colors as (R, G, B)
    "sweet": {
        "bg":       (255, 240, 245),   # soft pink
        "text":     (180, 80, 110),    # berry
        "quote":    (210, 150, 170),   # rose gold
    },
    "quotes": {
        "bg":       (255, 248, 225),   # cream
        "text":     (180, 90, 30),     # coklat tua
        "quote":    (220, 150, 60),    # emas/coklat muda
    },
    "dark": {
        "bg":       (30, 30, 40),      # dark navy
        "text":     (255, 255, 255),  # putih
        "quote":    (160, 160, 200),   # soft lavender
    },
    "blue": {
        "bg":       (230, 242, 255),   # soft sky
        "text":     (30, 80, 160),     # deep blue
        "quote":    (100, 150, 220),   # blue muted
    },
    "green": {
        "bg":       (230, 250, 235),   # soft mint
        "text":     (30, 130, 70),    # forest green
        "quote":    (100, 190, 130),   # green muted
    },
    "orange": {
        "bg":       (255, 245, 230),   # soft peach
        "text":     (200, 90, 20),     # deep orange
        "quote":    (255, 160, 60),    # orange bright
    },
    "purple": {
        "bg":       (245, 235, 255),   # soft lavender
        "text":     (110, 50, 170),    # deep purple
        "quote":    (170, 110, 220),  # purple muted
    },
    "red": {
        "bg":       (255, 235, 235),   # soft red
        "text":     (180, 40, 40),     # deep red
        "quote":    (255, 100, 100),  # red bright
    },
    "gold": {
        "bg":       (255, 248, 220),   # ivory
        "text":     (160, 110, 20),   # deep gold
        "quote":    (230, 180, 40),   # gold
    },
    "retro": {
        "bg":       (255, 220, 180),   # retro orange
        "text":     (120, 60, 20),     # coklat
        "quote":    (220, 130, 50),   # retro accent
    },
}


# ── Auto-detect mood dari teks ───────────────────────────────────────────────

def detect_mood(text: str) -> str:
    """Deteksi mood dari isi teks untuk pilih warna otomatis."""
    text_lower = text.lower()

    # Kata kunci mood
    mood_keywords = {
        "sweet":  ["love", "cinta", "sayang", "rindu", "miss", "hugs", "kiss", "terima kasih", "thank you", "sweet", "indah", "cantik", "imut", "lucu", "gemas", "senang", "bahagia", "happy", "fun", "laugh", "tertidur", "peaceful", "romantic", "mesra"],
        "quotes": ["quote", "pepatah", "katakan", "bilang", "fakta", "truth", "wisdom", "hikmah", "petuah", "motto", "inspir", "bijak", "deep", "深思", "buat apa", "kenapa", "memang", "sih", "titik", "tuh", "tapi", "padahal", "harus", "seharusnya", "mestinya", "logically"],
        "dark":   ["dark", "gabut", "nganggur", "bored", "nothing", "kosong", "sepi", "lonely", "sad", "sedih", "galau", "hujan", "rain", "night", "malam"],
        "blue":   ["sad", "sedih", "blue", "melankolis", "crying", "menangis", "hurt", "sakit hati", "patah", "broken", "baper", "overthinking"],
        "green":  ["fresh", "new", "baru", "growth", "tumbuh", "sukses", "success", "achievement", "goal", "target", "semangat", "motivated", "fitur", "update"],
        "orange": ["energi", "energy", "power", "fight", " semangat", "gaspoll", "passionate", "fire", "lava", "hot", "crazy"],
        "purple": ["magical", "misteri", "mystic", "gaib", "spiritual", "dream", "mimpi", "galaxy", "langit", "universe", "bintang"],
        "red":    ["marah", "angry", "geram", "kesal", "frustrasi", "stress", "panic", "panic", "b宜", "wtf", "argh", "bah", "huh", "tired", "capek"],
        "gold":   ["rich", "kaya", "sukses", "millioner", "winner", "juara", "champion", "legend", "king", "queen", "prime", "vip"],
        "retro":  ["retro", "vintage", "nostalgia", "old", "90an", "80an", "dulu", "kangen"],
    }

    # Scoring — use word boundaries to avoid substring false matches
    scores = {}
    for mood, keywords in mood_keywords.items():
        score = sum(1 for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', text_lower))
        if score > 0:
            scores[mood] = score

    if not scores:
        return "sweet"  # default fallback

    return max(scores, key=scores.get)


# ── Helpers ───────────────────────────────────────────────────────────────────

def hex_to_rgb(color: str) -> tuple:
    color = color.strip().lstrip('#')
    if len(color) == 6:
        return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
    return {
        'white':(255,255,255), 'black':(0,0,0), 'red':(255,0,0),
        'green':(0,128,0), 'blue':(0,0,255), 'yellow':(255,255,0),
        'orange':(255,165,0), 'purple':(128,0,128), 'pink':(255,192,203),
        'brown':(165,42,42), 'gray':(128,128,128), 'grey':(128,128,128),
        'cream':(255,248,225), 'navy':(30,30,60), 'gold':(255,215,0),
    }.get(color.lower(), (255,255,255))


def load_font(size: int, italic: bool = False):
    candidates = [
        '/System/Library/Fonts/Supplemental/Georgia Italic.ttf',
        '/System/Library/Fonts/Supplemental/Georgia Italic.ttf',
        '/System/Library/Fonts/Supplemental/Verdana Italic.ttf',
        '/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf',
        '/System/Library/Fonts/Supplemental/Trebuchet MS Italic.ttf',
        '/System/Library/Fonts/Supplemental/NewYorkItalic.ttf',
        '/System/Library/Fonts/SFCompactItalic.ttf',
        '/System/Library/Fonts/Helvetica.ttc',
        '/System/Library/Fonts/HelveticaNeue.ttc',
        '/Library/Fonts/Arial.ttf',
    ]
    for path in candidates:
        try:
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
        except:
            pass
    return ImageFont.load_default()


def rounded_rect(draw, xy, r, fill):
    x1, y1, x2, y2 = xy
    draw.rectangle([x1+r, y1, x2-r, y2], fill=fill)
    draw.rectangle([x1, y1+r, x2, y2-r], fill=fill)
    draw.pieslice([x1,y1,x1+2*r,y1+2*r], 180, 270, fill=fill)
    draw.pieslice([x2-2*r,y1,x2,y1+2*r], 270, 360, fill=fill)
    draw.pieslice([x1,y2-2*r,x1+2*r,y2], 90, 180, fill=fill)
    draw.pieslice([x2-2*r,y2-2*r,x2,y2], 0, 90, fill=fill)


# ── Mood descriptions ─────────────────────────────────────────────────────────

MOOD_LABELS = {
    "sweet":   "Sweet",
    "quotes":  "Pepatah",
    "dark":    "Dark",
    "blue":    "Blue",
    "green":   "Green",
    "orange":  "Energy",
    "purple":  "Mystic",
    "red":     "Frustrated",
    "gold":    "Success",
    "retro":   "Retro",
}


# ── Main Sticker Generator ──────────────────────────────────────────────────────

def make_sticker(
    text: str,
    bg_color: str = None,
    text_color: str = None,
    font_size: int = 38,
    output: str = './stiker.webp',
    canvas_size: int = 512,
    corner_radius: int = 70,
    mood: str = None,
    tagline: str = None,
    show_mood_label: bool = False,
) -> dict:
    """
    Generate a WhatsApp sticker with sweet quotes style.

    Returns dict with output path and detected mood.
    """
    # ── Auto-detect mood ──
    if mood and mood not in MOOD_PALETTES:
        mood = None

    detected_mood = mood or detect_mood(text)
    palette = MOOD_PALETTES[detected_mood]

    # ── Colors ──
    bg_rgb     = hex_to_rgb(bg_color) if bg_color else palette["bg"]
    text_rgb   = hex_to_rgb(text_color) if text_color else palette["text"]
    quote_rgb  = palette["quote"]

    # ── Fonts ──
    font_body = load_font(font_size, italic=True)
    font_quote = load_font(int(font_size * 3.4), italic=True)
    font_tag   = load_font(int(font_size * 0.72), italic=True)
    font_mood  = load_font(int(font_size * 0.5), italic=True)

    # ── Canvas ──
    img  = Image.new('RGBA', (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    rounded_rect(draw, [0, 0, canvas_size-1, canvas_size-1], corner_radius, bg_rgb)

    # ── Quote marks ──
    draw.text((40, 18), "\u201C", font=font_quote, fill=quote_rgb + (220,))
    draw.text((canvas_size-108, 18), "\u201D", font=font_quote, fill=quote_rgb + (220,))

    # ── Body text ──
    wrap_width = max(14, int(24 * (38 / font_size)))
    lines = textwrap.wrap(text, width=wrap_width)

    y = int(145 * (38 / font_size))
    line_spacing = int(10 * (38 / font_size))
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_body)
        w = bbox[2] - bbox[0]
        x = (canvas_size - w) // 2
        draw.text((x, y), line, font=font_body, fill=text_rgb + (255,))
        y += bbox[3] - bbox[1] + line_spacing

    # ── Separator line ──
    line_y = y + int(20 * (38 / font_size))
    draw.line([(100, line_y), (canvas_size-100, line_y)], fill=quote_rgb + (160,), width=2)

    # ── Tagline ──
    tag_text = tagline or f"— {MOOD_LABELS.get(detected_mood, 'Someone')}"
    bbox = draw.textbbox((0, 0), tag_text, font=font_tag)
    w = bbox[2] - bbox[0]
    x = (canvas_size - w) // 2
    draw.text((x, line_y + 14), tag_text, font=font_tag, fill=text_rgb + (200,))

    # ── Mood label (small, bottom-right corner) ──
    if show_mood_label:
        mood_text = detected_mood.upper()
        bbox_m = draw.textbbox((0, 0), mood_text, font=font_mood)
        mx = canvas_size - bbox_m[2] - bbox_m[0] - 18
        my = canvas_size - bbox_m[3] - bbox_m[1] - 14
        draw.text((mx, my), mood_text, font=font_mood, fill=quote_rgb + (130,))

    # ── Save ──
    img.save(output, 'WEBP', quality=92)

    return {
        "output_path": output,
        "detected_mood": detected_mood,
        "palette_used": palette,
        "mood_label": MOOD_LABELS.get(detected_mood, 'Someone'),
    }


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Generate WhatsApp sticker — sweet quote style, auto mood detection'
    )
    parser.add_argument('--text', '-t', required=True, help='Text for the sticker')
    parser.add_argument('--bg-color', '-b', default=None, help='Background color (overrides mood)')
    parser.add_argument('--text-color', '-c', default=None, help='Text color (overrides mood)')
    parser.add_argument('--font-size', '-s', type=int, default=38, help='Body font size in px')
    parser.add_argument('--output', '-o', default='./stiker.webp', help='Output .webp path')
    parser.add_argument('--canvas-size', type=int, default=512, help='Canvas size (square)')
    parser.add_argument('--corner-radius', type=int, default=70, help='Corner radius')
    parser.add_argument('--mood', '-m', default=None,
        help=f"Mood palette: {', '.join(MOOD_PALETTES.keys())}. Auto-detect if omitted.")
    parser.add_argument('--tagline', default=None, help='Override tagline (e.g. "-- Anonymous")')
    parser.add_argument('--show-mood', action='store_true', help='Show mood label in corner')

    args = parser.parse_args()

    try:
        result = make_sticker(
            text=args.text,
            bg_color=args.bg_color,
            text_color=args.text_color,
            font_size=args.font_size,
            output=args.output,
            canvas_size=args.canvas_size,
            corner_radius=args.corner_radius,
            mood=args.mood,
            tagline=args.tagline,
            show_mood_label=args.show_mood,
        )
        print(f'STICKER_SAVED:{result["output_path"]}')
        print(f'MOOD_DETECTED:{result["detected_mood"]} ({result["mood_label"]})')
        print(f'PALETTE_BG:{result["palette_used"]["bg"]}')
        print(f'PALETTE_TEXT:{result["palette_used"]["text"]}')
    except Exception as e:
        print(f'ERROR:{e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
