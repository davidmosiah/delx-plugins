from PIL import Image, ImageDraw

S = 6  # supersample

def path(draw, W, spread_y, color, width):
    """Paths fan in from the left, meet at the centre node, fan out to the right.
    Divergent work converging into one continuous thread — then continuing."""
    cx = cy = W * 0.5
    pts = []
    for i in range(101):
        t = i / 100
        e = t * t * (3 - 2 * t)          # ease into the node
        pts.append((t * cx, spread_y + (cy - spread_y) * e))
    for i in range(1, 101):
        t = i / 100
        e = t * t * (3 - 2 * t)          # ease back out, tighter
        pts.append((cx + t * cx, cy + (spread_y - cy) * e * 0.42))
    draw.line(pts, fill=color, width=width, joint="curve")

def make(size, bg, lines, accent, out, n=5, stroke=0.016, dot=0.10):
    W = size * S
    im = Image.new("RGBA", (W, W), bg)
    d = ImageDraw.Draw(im)
    spreads = [0.14, 0.30, 0.50, 0.70, 0.86] if n == 5 else [0.20, 0.50, 0.80]
    for i, f in enumerate(spreads):
        path(d, W, f * W, lines[i % len(lines)], max(2, int(W * stroke)))
    r = W * dot / 2
    d.ellipse([W*0.5 - r, W*0.5 - r, W*0.5 + r, W*0.5 + r], fill=accent)
    im.resize((size, size), Image.LANCZOS).save(out)
    print(f"{out}: {size}x{size}")

DARK_BG  = (10, 10, 15, 255)
LIGHT_BG = (250, 250, 252, 255)
CYAN     = (34, 211, 238, 255)
TEAL     = (13, 148, 176, 255)
DARK_L   = [(96, 125, 205, 255), (128, 105, 225, 245), (70, 160, 200, 255), (118, 118, 215, 240), (88, 138, 205, 250)]
LIGHT_L  = [(46, 66, 150, 255), (82, 56, 170, 245), (28, 100, 140, 255), (66, 66, 160, 240), (42, 82, 150, 250)]

make(256, DARK_BG,  DARK_L,  CYAN, "icon-dark-256.png")
make(256, LIGHT_BG, LIGHT_L, TEAL, "icon-light-256.png")
make(48,  DARK_BG,  DARK_L,  CYAN, "icon-composer-48.png", n=3, stroke=0.040, dot=0.20)
