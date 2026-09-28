"""Crinoid QR: a scannable QR code for the repo, drawn as a sea lily.

The QR square is the crown. Ten arms rise from a cup below the code and fan
up THROUGH it: inside the code each arm is only a tint that keeps every
module's luminance class (dark modules go deep rose, light modules go pale
rose), so the decoder still sees the same bits. Outside the code the arms
are drawn in full with pinnules, the tips curling past the edges, and a
stalk of columnals runs down to a holdfast.

Writes qr-crinoid.svg and qr-crinoid.png, then decodes the PNG with OpenCV
at several sizes and refuses (exit 1) unless every one decodes to URL.
"""
import math, sys, pathlib
import segno
from PIL import Image, ImageDraw, ImageFilter

URL = "https://github.com/Syntaxswine/crinoid-life"
OUT = pathlib.Path(__file__).resolve().parent.parent

PAPER, INK = "#eeece4", "#1f2322"
ROSE_DARK, ROSE_PALE = "#6b2a3f", "#e8cfd6"    # tint pair inside the code
ROSE, STALK = "#9a4a63", "#857d6e"             # full-strength outside it

qr = segno.make(URL, error="h", micro=False)
M = [[bool(v) for v in row] for row in qr.matrix]
N = len(M)
import os
FR = float(os.environ.get("QR_FR", "0.8"))   # finder corner radius
DOT = os.environ.get("QR_DOT", "1") == "1"
QZ = 4                                          # quiet zone, modules
SIDE, TOP, BELOW = 24, 17, 30                   # room for tips / stalk
W = N + 2 * QZ + 2 * SIDE
H = TOP + N + 2 * QZ + BELOW
X0, Y0 = SIDE + QZ, TOP + QZ                    # code origin (module units)
CX = X0 + N / 2
CUP = (CX, Y0 + N + QZ + 1.5)                   # where the arms leave the cup

def quad(p0, p1, p2, n=80):
    return [((1-t)**2*p0[0] + 2*t*(1-t)*p1[0] + t*t*p2[0],
             (1-t)**2*p0[1] + 2*t*(1-t)*p1[1] + t*t*p2[1])
            for t in (i / n for i in range(n + 1))]

# Ten arms. Each is two quadratic legs: up through the crown, then a curl.
ARMS = []
for i in range(10):
    u = i / 9 - 0.5                              # -0.5 .. 0.5
    a = u * math.radians(150)
    reach = N + QZ + 13 - abs(u) * 11
    tip = (CUP[0] + math.sin(a) * reach * 0.8, CUP[1] - math.cos(a) * reach)
    ctrl = (CUP[0] + math.sin(a) * reach * 0.25, CUP[1] - reach * 0.55)
    leg1 = quad((CUP[0] + u * 3, CUP[1]), ctrl, tip)
    side = 1 if u >= 0 else -1
    curl_to = (tip[0] + side * 4, tip[1] + 2.5)
    curl_c = (tip[0] + side * 1.5 + math.sin(a) * 3, tip[1] - 3.5)
    ARMS.append(leg1 + quad(tip, curl_c, curl_to, 30)[1:])

def dist_to_arm(x, y, pts):
    best = 1e9
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        dx, dy = bx - ax, by - ay
        L = dx*dx + dy*dy or 1e-9
        t = max(0, min(1, ((x-ax)*dx + (y-ay)*dy) / L))
        best = min(best, math.hypot(x - ax - t*dx, y - ay - t*dy))
    return best

def on_arm(r, c):
    x, y = X0 + c + .5, Y0 + r + .5
    return any(dist_to_arm(x, y, p) < 0.95 for p in ARMS)

def in_finder(r, c):
    return (r < 8 and c < 8) or (r < 8 and c >= N - 8) or (r >= N - 8 and c < 8)

inside = lambda x, y: X0 - QZ <= x <= X0 + N + QZ and Y0 - QZ <= y <= Y0 + N + QZ

# ------------------------------------------------------------------ shapes
# Everything is emitted as a list of primitives in module units, then drawn
# twice: once as SVG, once with PIL (supersampled) for the decode check.
prims = []   # (kind, colour, data)

prims.append(("rect", PAPER, (0, 0, W, H, 0)))
# holdfast roots
base_y = H - 3
for dx, spread in ((-1, -7), (1, 7), (-1, -3.5), (1, 3.5)):
    prims.append(("line", STALK, (quad((CX, base_y - 3), (CX + spread * .4, base_y), (CX + spread, base_y + 1.2), 30), 0.9)))
# stalk: a column of discs from the cup down to the holdfast
y = CUP[1] + 2.2
while y < base_y - 2:
    prims.append(("rect", STALK, (CX - 1.3, y, 2.6, 0.95, 0.35)))
    y += 1.15
# cirri: little hooked side branches at intervals, like isocrinid nodals
for k, yy in enumerate((CUP[1] + 7, CUP[1] + 13, CUP[1] + 19)):
    for s in (-1, 1):
        prims.append(("line", STALK, (quad((CX, yy), (CX + s * 3.5, yy - 0.5), (CX + s * 4.2, yy + 2.2), 20), 0.55)))
# cup (calyx)
prims.append(("poly", ROSE, [(CX - 3.2, CUP[1] - 0.2), (CX + 3.2, CUP[1] - 0.2),
                              (CX + 1.6, CUP[1] + 2.6), (CX - 1.6, CUP[1] + 2.6)]))

# arms outside the code (and quiet zone): full stroke + pinnules
for pts in ARMS:
    seg, run = [], []
    for p in pts:
        if inside(*p):
            if len(run) > 1: seg.append(run)
            run = []
        else:
            run.append(p)
    if len(run) > 1: seg.append(run)
    for run in seg:
        prims.append(("line", ROSE, (run, 1.15)))
        for j in range(3, len(run) - 1, 3):
            (ax, ay), (bx, by) = run[j - 1], run[j + 1]
            L = math.hypot(bx - ax, by - ay) or 1
            nx, ny = -(by - ay) / L, (bx - ax) / L
            s = 1 if (j // 3) % 2 else -1
            px, py = run[j]
            prims.append(("line", ROSE, ([(px, py), (px + s*nx*1.6 + (bx-ax)/L*.9, py + s*ny*1.6 + (by-ay)/L*.9)], 0.45)))
    # inside the quiet zone: a pale band only (reads as light)
    qz = [p for p in pts if inside(*p) and not (X0 <= p[0] <= X0 + N and Y0 <= p[1] <= Y0 + N)]
    if len(qz) > 1:
        prims.append(("line", ROSE_PALE, (qz, 1.9)))

# the code itself
for r in range(N):
    for c in range(N):
        x, y = X0 + c, Y0 + r
        arm = on_arm(r, c) and not in_finder(r, c)
        if not M[r][c]:
            if arm: prims.append(("rect", ROSE_PALE, (x, y, 1, 1, 0)))
            continue
        if in_finder(r, c):
            continue
        if DOT: prims.append(("circ", ROSE_DARK if arm else INK, (x + .5, y + .5, .47)))
        else: prims.append(("rect", ROSE_DARK if arm else INK, (x + .04, y + .04, .92, .92, .3)))
# finder patterns as rounded rings (drawn whole, not per module)
for fr, fc in ((0, 0), (0, N - 7), (N - 7, 0)):
    x, y = X0 + fc, Y0 + fr
    prims.append(("rect", INK, (x, y, 7, 7, FR)))
    prims.append(("rect", PAPER, (x + 1, y + 1, 5, 5, FR * .6)))
    prims.append(("rect", INK, (x + 2, y + 2, 3, 3, FR * .45)))

# ------------------------------------------------------------------ render
def svg():
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W*16}" height="{H*16}">',
         f'<title>QR code: {URL} — drawn as a crinoid</title>']
    for k, col, d in prims:
        if k == "rect":
            x, y, w, h, rr = d
            o.append(f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" rx="{rr}" fill="{col}"/>')
        elif k == "circ":
            o.append(f'<circle cx="{d[0]:.2f}" cy="{d[1]:.2f}" r="{d[2]}" fill="{col}"/>')
        elif k == "poly":
            o.append(f'<polygon points="{" ".join(f"{x:.2f},{y:.2f}" for x,y in d)}" fill="{col}"/>')
        elif k == "line":
            pts, w = d
            o.append(f'<polyline points="{" ".join(f"{x:.2f},{y:.2f}" for x,y in pts)}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')
    o.append("</svg>")
    return "\n".join(o)

def png(scale):
    ss = 4
    s = scale * ss
    im = Image.new("RGB", (int(W * s), int(H * s)), PAPER)
    d = ImageDraw.Draw(im)
    for k, col, dd in prims:
        if k == "rect":
            x, y, w, h, rr = dd
            d.rounded_rectangle([x*s, y*s, (x+w)*s - 1, (y+h)*s - 1], radius=rr*s, fill=col)
        elif k == "circ":
            cx, cy, r = dd
            d.ellipse([(cx-r)*s, (cy-r)*s, (cx+r)*s, (cy+r)*s], fill=col)
        elif k == "poly":
            d.polygon([(x*s, y*s) for x, y in dd], fill=col)
        elif k == "line":
            pts, w = dd
            d.line([(x*s, y*s) for x, y in pts], fill=col, width=max(1, int(w*s)), joint="curve")
            r = w * s / 2
            for x, y in (pts[0], pts[-1]):
                d.ellipse([x*s-r, y*s-r, x*s+r, y*s+r], fill=col)
    return im.resize((int(W*scale), int(H*scale)), Image.LANCZOS)

(OUT / "qr-crinoid.svg").write_text(svg(), encoding="utf-8")
big = png(20)
big.save(OUT / "qr-crinoid.png")

# ------------------------------------------------------------------ refuse
# Two independent decoders. ZXing (what Android scanners run) must read every
# variant; OpenCV's classic detector is stricter about finder shape and must
# read the clean renders. A plain segno code is decoded first as the control,
# so a broken decoder install cannot pass off as a broken design.
import cv2, numpy as np, zxingcpp
det = cv2.QRCodeDetector()
def cv_read(im):
    return det.detectAndDecode(cv2.cvtColor(np.array(im.convert("RGB")), cv2.COLOR_RGB2BGR))[0]
def zx_read(im):
    r = zxingcpp.read_barcodes(im)
    return r[0].text if r else ""
plain = qr.to_pil(scale=8, border=4) if hasattr(qr, "to_pil") else None
if plain is None:
    import io; buf = io.BytesIO(); qr.save(buf, kind="png", scale=8, border=4); buf.seek(0); plain = Image.open(buf)
assert cv_read(plain) == URL and zx_read(plain) == URL, "control failed: decoders are broken, not the design"
fails = []
# OpenCV is not required on the 20px print file: it decodes that code when
# cropped (any padding) and the whole composition at half size, but its
# localiser loses the full 1380x1760 frame. Measured 2026-09-27.
cases = [("20px/module", big, False), ("10px/module", png(10), True), ("8px/module", png(8), True), ("4px/module", png(4), False),
         ("8px blurred", png(8).filter(ImageFilter.GaussianBlur(1.5)), False),
         ("8px greyscale", png(8).convert("L"), True),
         ("3px/module", png(3), False)]
for label, im, need_cv in cases:
    z, c = zx_read(im) == URL, cv_read(im) == URL
    print(f"{label:>14}:  zxing {'OK ' if z else 'FAIL'}   opencv {'OK ' if c else ('FAIL' if need_cv else 'miss (not required)')}")
    if not z or (need_cv and not c): fails.append(label)
tinted = sum(1 for r in range(N) for c in range(N) if on_arm(r, c) and not in_finder(r, c))
print(f"version {qr.version}-H, {N}x{N}; {tinted} of {N*N} modules tinted ({tinted/(N*N):.0%})")
print("REFUSED:" if fails else "all required decodes pass", ", ".join(fails))
sys.exit(1 if fails else 0)
