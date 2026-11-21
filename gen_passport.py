"""Draws an open passport spread for the invented Republic of Veldara -> entry.png"""
import os, random, math, datetime as dt
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

S = 2
W, H = 1024 * S, 724 * S
M = 14 * S
rnd = random.Random(20261121)
F = r"C:\Windows\Fonts"
def font(n, px):
    return ImageFont.truetype(os.path.join(F, n), int(px * S))

# ---------- data ----------
TODAY = dt.date(2026, 11, 21)
ISSUE = dt.date(2023, 3, 14)
EXPIRY = dt.date(2033, 3, 13)
DOB = dt.date(1988, 7, 9)
assert EXPIRY == ISSUE.replace(year=ISSUE.year + 10) - dt.timedelta(days=1)
def dm(d): return d.strftime("%d %b %Y").upper()
def yymmdd(d): return d.strftime("%y%m%d")

SURNAME, GIVEN = "ORMELIN", "TAVIA SERENE"
PNO, CODE, SEX = "VL4829315", "VLD", "F"
PERSONAL = "MR7K2P0412"

def cd(s):
    vals = {"<": 0}
    for i in range(10): vals[str(i)] = i
    for i in range(26): vals[chr(65 + i)] = 10 + i
    w = [7, 3, 1]
    return str(sum(vals[c] * w[i % 3] for i, c in enumerate(s)) % 10)

l1 = ("P<" + CODE + SURNAME + "<<" + GIVEN.replace(" ", "<")).ljust(44, "<")
pn = PERSONAL.ljust(14, "<")
l2 = PNO + cd(PNO) + CODE + yymmdd(DOB) + cd(yymmdd(DOB)) + SEX + yymmdd(EXPIRY) + cd(yymmdd(EXPIRY)) + pn + cd(pn)
l2 += cd(l2[0:10] + l2[13:20] + l2[21:43])
assert len(l1) == 44 and len(l2) == 44
assert l2[0:9] == PNO and l2[13:19] == yymmdd(DOB) and l2[21:27] == yymmdd(EXPIRY)

# stamps: (neighbour/post, kind, date)
D = dt.date
STAMPS = [
    ("KESTAVIA", "Harrowgate Bridge", "ENTRY", D(2024, 6, 2)),
    ("KESTAVIA", "Harrowgate Bridge", "EXIT", D(2024, 6, 19)),
    ("VELDARA", "Rhune Lock 19", "ENTRY", D(2024, 6, 19)),
    ("DUNMOOR", "Skarn Quay", "ENTRY", D(2024, 9, 11)),
    ("DUNMOOR", "Skarn Quay", "EXIT", D(2024, 9, 15)),
    ("VELDARA", "Marenhal Port", "ENTRY", D(2024, 9, 16)),
]
for s in STAMPS: assert ISSUE < s[3] < TODAY
for a, b in [(0, 1), (3, 4)]:
    assert STAMPS[a][3] < STAMPS[b][3] and STAMPS[a][0] == STAMPS[b][0]
assert STAMPS[1][3] <= STAMPS[2][3] < STAMPS[3][3] and STAMPS[4][3] <= STAMPS[5][3]
VISA_DATE = D(2024, 5, 28)
PERMIT_DATE = D(2024, 9, 9)
assert ISSUE < VISA_DATE < STAMPS[0][3] and STAMPS[2][3] < PERMIT_DATE < STAMPS[3][3]
VISA_FROM, VISA_TO = D(2024, 6, 1), D(2024, 6, 30)
assert VISA_FROM <= STAMPS[0][3] and STAMPS[1][3] <= VISA_TO

# ---------- canvas ----------
img = Image.new("RGB", (W, H), (38, 30, 26))
d = ImageDraw.Draw(img)
mid = W // 2
LP = (M, M, mid, H - M)
RP = (mid, M, W - M, H - M)
cur = [None]
def T(dr, xy, s, f, fill, anchor="la", check=True):
    dr.text(xy, s, font=f, fill=fill, anchor=anchor)
    if check and cur[0]:
        b = dr.textbbox(xy, s, font=f, anchor=anchor)
        p = cur[0]
        assert b[0] >= p[0] + 8 and b[2] <= p[2] - 8 and b[1] >= p[1] + 8 and b[3] <= p[3] - 8, (s, b, p)
        assert f.size >= 9 * S

# paper
def paper(box, tint):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=tint)
paper(LP, (236, 230, 214))
paper(RP, (240, 228, 200))

# right page security pattern: fine lines + guilloche
pat = Image.new("RGBA", (W, H), (0, 0, 0, 0))
pd = ImageDraw.Draw(pat)
for y in range(RP[1] + 4, RP[3] - 4, 6):
    pd.line([(RP[0] + 4, y), (RP[2] - 4, y)], fill=(150, 175, 160, 34), width=1)
cx0, cy0 = (RP[0] + RP[2]) // 2, (RP[1] + RP[3]) // 2 - 60
for k in range(36):
    a = k * math.pi / 18
    pts = []
    for t in range(0, 361, 4):
        r = 230 + 40 * math.sin(math.radians(t * 7 + k * 10))
        pts.append((cx0 + r * math.cos(math.radians(t)) * 1.1, cy0 + r * math.sin(math.radians(t)) * 0.9))
    pd.line(pts, fill=(120, 150, 140, 22), width=1)
img.paste(pat, (0, 0), pat)
d = ImageDraw.Draw(img)

# left page ruled lines + number
for y in range(LP[1] + 60, LP[3] - 40, 28):
    d.line([(LP[0] + 40, y), (LP[2] - 36, y)], fill=(205, 200, 188), width=1)
cur[0] = LP
T(d, (LP[0] + 110, LP[3] - 30), "14", font("times.ttf", 14), (90, 85, 78), "mm")
T(d, ((LP[0] + LP[2]) // 2, LP[1] + 26), "VISAS · VIZAT · ENDORSEMENTS", font("segoeuib.ttf", 10), (120, 110, 100), "mm")

# ---------- stamp helper ----------
def speckle(layer, alpha_base):
    w, h = layer.size
    noise = Image.frombytes("L", (w, h), rnd.randbytes(w * h))
    noise = noise.point(lambda v: 255 if v > 40 else 150).filter(ImageFilter.GaussianBlur(0.8))
    a = layer.getchannel("A")
    a = ImageChops.multiply(a, noise)
    a = a.point(lambda v: int(v * alpha_base))
    layer.putalpha(a)

def place(layer, cx, cy, ang):
    layer = layer.rotate(ang, resample=Image.BICUBIC, expand=True)
    img.paste(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)), layer)

def stamp_round(cx, cy, post, country, kind, date, col, ang, r=64, alpha=0.86):
    r *= S
    n = 2 * r + 20
    L = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    g = ImageDraw.Draw(L)
    c = n // 2
    g.ellipse((c - r, c - r, c + r, c + r), outline=col + (255,), width=3 * S)
    g.ellipse((c - r + 8 * S, c - r + 8 * S, c + r - 8 * S, c + r - 8 * S), outline=col + (255,), width=1 * S)
    T(g, (c, c - r * 0.52), country, font("segoeuib.ttf", 11), col + (255,), "mm", False)
    T(g, (c, c - 12 * S), post.upper(), font("segoeuib.ttf", 9.5), col + (255,), "mm", False)
    g.line([(c - r * 0.8, c - 2 * S), (c + r * 0.8, c - 2 * S)], fill=col + (255,), width=1 * S)
    T(g, (c, c + 13 * S), dm(date), font("consolab.ttf", 13), col + (255,), "mm", False)
    g.line([(c - r * 0.8, c + 26 * S), (c + r * 0.8, c + 26 * S)], fill=col + (255,), width=1 * S)
    T(g, (c, c + r * 0.6), kind, font("segoeuib.ttf", 12), col + (255,), "mm", False)
    arrow = (c + r * 0.62, c + r * 0.62)
    speckle(L, alpha)
    place(L, cx, cy, ang)

def stamp_rect(cx, cy, w, h, lines, col, ang, bold_idx=0, alpha=0.86, double=True):
    w *= S; h *= S
    n_w, n_h = w + 20, h + 20
    L = Image.new("RGBA", (n_w, n_h), (0, 0, 0, 0))
    g = ImageDraw.Draw(L)
    g.rectangle((10, 10, 10 + w, 10 + h), outline=col + (255,), width=3 * S)
    if double:
        g.rectangle((10 + 6 * S, 10 + 6 * S, 10 + w - 6 * S, 10 + h - 6 * S), outline=col + (255,), width=1 * S)
    y = 10 + h / (len(lines) + 1)
    for i, s in enumerate(lines):
        f = font("segoeuib.ttf", 12) if i == bold_idx else font("consolab.ttf", 12)
        T(g, (10 + w / 2, y), s, f, col + (255,), "mm", False)
        y += h / (len(lines) + 1)
    speckle(L, alpha)
    place(L, cx, cy, ang)

def stamp_oval(cx, cy, w, h, post, country, kind, date, col, ang, alpha=0.84):
    w *= S; h *= S
    L = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
    g = ImageDraw.Draw(L)
    g.ellipse((10, 10, 10 + w, 10 + h), outline=col + (255,), width=3 * S)
    g.ellipse((10 + 7 * S, 10 + 7 * S, 10 + w - 7 * S, 10 + h - 7 * S), outline=col + (255,), width=1 * S)
    cxl, cyl = 10 + w / 2, 10 + h / 2
    T(g, (cxl, cyl - h * 0.27), country, font("segoeuib.ttf", 11), col + (255,), "mm", False)
    T(g, (cxl, cyl - h * 0.09), post.upper(), font("segoeuib.ttf", 9.5), col + (255,), "mm", False)
    T(g, (cxl, cyl + h * 0.1), dm(date), font("consolab.ttf", 13), col + (255,), "mm", False)
    T(g, (cxl, cyl + h * 0.28), kind, font("segoeuib.ttf", 12), col + (255,), "mm", False)
    speckle(L, alpha)
    place(L, cx, cy, ang)

BLUE, VIOL, RED, BLK = (36, 62, 140), (96, 52, 140), (170, 36, 40), (40, 40, 46)
lx = LP[0]
# visa box (printed sticker-like)
def printed_box(x0, y0, x1, y1, title, rows, col=(60, 70, 95)):
    d.rectangle((x0, y0, x1, y1), outline=col, width=2 * S)
    d.rectangle((x0 + 4 * S, y0 + 4 * S, x1 - 4 * S, y1 - 4 * S), outline=col, width=1)
    T(d, (x0 + 12 * S, y0 + 10 * S), title, font("segoeuib.ttf", 10), col)
    y = y0 + 28 * S
    for a, b in rows:
        T(d, (x0 + 12 * S, y), a, font("segoeui.ttf", 9), (100, 100, 105))
        T(d, (x0 + 12 * S + 70 * S, y), b, font("consolab.ttf", 11), (40, 40, 50))
        y += 16 * S

# Kestavia visa sticker
printed_box(lx + 46 * S, M + 46 * S, lx + 262 * S, M + 140 * S, "KESTAVIA · VISA / VIZA",
            [("TYPE", "TRANSIT-RIVER 30D"), ("ISSUED", dm(VISA_DATE)), ("VALID", dm(VISA_FROM)[:6] + "-" + dm(VISA_TO)),
             ("PLACE", "Marenhal")])
# telling detail: barge endorsement (on left page, Veldaran/English)
printed_box(lx + 46 * S, M + 372 * S, lx + 262 * S, M + 462 * S, "PERMIT · LEUBA · BARGE CREW",
            [("RIVER", "RHUNE LOCKS 4-19"), ("HOURS", "DAYLIGHT ONLY"), ("FEE", "45 KRONE · PAID"), ("ISSUED", dm(PERMIT_DATE))],
            col=(120, 40, 50))

# stamps
stamp_round(lx + 340 * S, M + 90 * S, "Harrowgate Br.", "KESTAVIA", "ENTRY", STAMPS[0][3], BLUE, -9)
stamp_oval(lx + 395 * S, M + 235 * S, 150, 96, "Harrowgate Br.", "KESTAVIA", "EXIT", STAMPS[1][3], VIOL, 8)
stamp_rect(lx + 150 * S, M + 255 * S, 150, 78, ["VELDARA", "RHUNE LOCK 19", dm(STAMPS[2][3]), "ENTRY · VHOD"], RED, -4, 0)
stamp_round(lx + 380 * S, M + 380 * S, "Skarn Quay", "DUNMOOR", "ENTRY", STAMPS[3][3], BLK, 6, r=58)
stamp_rect(lx + 330 * S, M + 495 * S, 160, 82, ["DUNMOOR · SKARN QUAY", dm(STAMPS[4][3]), "DEPARTED · EXIT"], BLUE, -7, 0)
stamp_round(lx + 140 * S, M + 565 * S, "Marenhal Port", "VELDARA", "ENTRY", STAMPS[5][3], RED, 11, r=62)

# ---------- right page: data page ----------
cur[0] = RP
rx0, rx1 = RP[0] + 34 * S, RP[2] - 30 * S
ink = (30, 32, 44)
lab = (96, 96, 108)
# watermark
wm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
wd = ImageDraw.Draw(wm)
wcx, wcy = (RP[0] + RP[2]) // 2 + 90 * S, (RP[1] + RP[3]) // 2 - 10 * S
wd.ellipse((wcx - 90 * S, wcy - 90 * S, wcx + 90 * S, wcy + 90 * S), outline=(150, 160, 140, 45), width=3 * S)
wd.ellipse((wcx - 70 * S, wcy - 70 * S, wcx + 70 * S, wcy + 70 * S), outline=(150, 160, 140, 40), width=1 * S)
T(wd, (wcx, wcy), "VLD", font("georgiab.ttf", 52), (150, 160, 140, 50), "mm", False)
img.paste(wm, (0, 0), wm)
d = ImageDraw.Draw(img)

# header: emblem
ex, ey = rx0 + 24 * S, RP[1] + 46 * S
gold = (150, 112, 40)
d.ellipse((ex - 20 * S, ey - 20 * S, ex + 20 * S, ey + 20 * S), outline=ink, width=2 * S)
d.polygon([(ex - 11 * S, ey - 12 * S), (ex + 11 * S, ey - 12 * S), (ex + 11 * S, ey + 2 * S), (ex, ey + 14 * S), (ex - 11 * S, ey + 2 * S)], outline=ink, width=2 * S)
d.line([(ex - 11 * S, ey - 2 * S), (ex + 11 * S, ey - 2 * S)], fill=ink, width=1 * S)
d.polygon([(ex - 10 * S, ey + 1 * S), (ex - 4 * S, ey + 5 * S), (ex, ey + 1 * S), (ex + 4 * S, ey + 5 * S), (ex + 10 * S, ey + 1 * S), (ex + 10 * S, ey + 4 * S), (ex, ey + 9 * S), (ex - 10 * S, ey + 4 * S)], fill=(60, 90, 140))
d.line([(ex, ey - 24 * S), (ex, ey - 12 * S)], fill=ink, width=2 * S)
d.polygon([(ex, ey - 22 * S), (ex + 9 * S, ey - 19 * S), (ex, ey - 16 * S)], fill=(150, 40, 40))
hx = (rx0 + rx1) // 2 + 22 * S
T(d, (hx, RP[1] + 34 * S), "REPUBLIKA VELDARA · REPUBLIC OF VELDARA", font("georgiab.ttf", 13), ink, "mm")
T(d, (hx, RP[1] + 56 * S), "PASAPORTA · PASSPORT", font("georgiab.ttf", 17), ink, "mm")
d.line([(rx0, RP[1] + 76 * S), (rx1, RP[1] + 76 * S)], fill=ink, width=2)

# portrait
px0, py0 = rx0, RP[1] + 90 * S
pw, ph = 150 * S, 190 * S
port = Image.new("RGB", (pw, ph), (150, 165, 175))
pg = ImageDraw.Draw(port)
for y in range(ph):
    t = y / ph
    pg.line([(0, y), (pw, y)], fill=(int(165 - 30 * t), int(178 - 30 * t), int(188 - 30 * t)))
cxp = pw // 2
pg.ellipse((cxp - 78 * S, ph - 60 * S, cxp + 78 * S, ph + 70 * S), fill=(48, 58, 74))        # shoulders
pg.polygon([(cxp - 18 * S, ph - 62 * S), (cxp + 18 * S, ph - 62 * S), (cxp, ph - 34 * S)], fill=(225, 225, 228))  # collar
pg.rectangle((cxp - 14 * S, ph - 100 * S, cxp + 14 * S, ph - 60 * S), fill=(176, 142, 120))   # neck
pg.ellipse((cxp - 42 * S, 28 * S, cxp + 42 * S, 120 * S), fill=(96, 70, 52))                  # hair back
pg.ellipse((cxp - 34 * S, 42 * S, cxp + 34 * S, ph - 70 * S), fill=(190, 154, 130))           # face
pg.pieslice((cxp - 40 * S, 30 * S, cxp + 40 * S, 100 * S), 180, 360, fill=(96, 70, 52))       # fringe
for sx in (-14, 14):
    pg.ellipse((cxp + sx * S - 4 * S, 82 * S, cxp + sx * S + 4 * S, 88 * S), fill=(40, 34, 32))
pg.line([(cxp, 90 * S), (cxp - 2 * S, 106 * S)], fill=(160, 124, 102), width=2 * S)
pg.line([(cxp - 9 * S, 120 * S), (cxp + 9 * S, 120 * S)], fill=(130, 70, 66), width=2 * S)
port = Image.blend(port, Image.new("RGB", port.size, (120, 130, 140)), 0.12)
port = port.convert("L").convert("RGB")
tone = Image.new("RGB", port.size, (70, 95, 120))
port = ImageChops.screen(ImageChops.multiply(port, Image.new("RGB", port.size, (190, 205, 225))), Image.new("RGB", port.size, (15, 20, 28)))
img.paste(port, (px0, py0))
d = ImageDraw.Draw(img)
d.rectangle((px0, py0, px0 + pw, py0 + ph), outline=ink, width=2 * S)
# ghost portrait
gp = port.resize((52 * S, 66 * S)).convert("L")
gl = Image.new("RGBA", gp.size, (110, 120, 110, 0))
gl.putalpha(gp.point(lambda v: 90))
gx, gy = px0 + pw + 8 * S, py0 + ph - 66 * S
img.paste(Image.new("RGB", gp.size, (170, 170, 150)), (gx, gy), gl.getchannel("A"))
d = ImageDraw.Draw(img)
# small photo-like detail: pointed micro-photo with tilt mark
d.rectangle((gx, py0, gx + 52 * S, py0 + 40 * S), outline=lab, width=1)
T(d, (gx + 26 * S, py0 + 20 * S), "VLD", font("georgiab.ttf", 14), (150, 150, 140), "mm")
d.rectangle((gx, py0 + 46 * S, gx + 52 * S, py0 + 112 * S), outline=lab, width=1)
T(d, (gx + 26 * S, py0 + 79 * S), "P", font("georgiab.ttf", 26), (170, 170, 160), "mm")

# fields
fx0 = gx + 52 * S + 14 * S
colw = (rx1 - fx0) // 2
fl, fv = font("segoeui.ttf", 9), font("consolab.ttf", 13)
def field(col, row, label, value, span=1):
    x = fx0 + col * colw
    y = py0 + row * 38 * S
    T(d, (x, y), label, fl, lab)
    T(d, (x, y + 11 * S), value, fv, ink)
field(0, 0, "TIP / TYPE", "P")
field(1, 0, "KOD / CODE", CODE)
field(0, 1, "PASAPORTA No. / PASSPORT No.", PNO)
field(1, 1, "DRZAVA / NATIONALITY", "VELDARAN")
d.line([(fx0, py0 + 80 * S), (rx1, py0 + 80 * S)], fill=(190, 185, 170), width=1)
# wide fields below the portrait
fx0 = rx0 + 160 * S + 0
fy = py0 + ph + 10 * S
fx0 = rx0
colw = (rx1 - rx0) // 2
def field2(col, row, label, value):
    x = rx0 + col * colw
    y = fy + row * 38 * S
    T(d, (x, y), label, fl, lab)
    T(d, (x, y + 11 * S), value, fv, ink)
# row set below
field2(0, 0, "PRIIMEK / SURNAME", SURNAME)
field2(1, 0, "IMENA / GIVEN NAMES", GIVEN)
field2(0, 1, "ROJSTVO / DATE OF BIRTH", dm(DOB))
field2(1, 1, "SPOL / SEX", SEX)
field2(0, 2, "KRAJ ROJSTVA / PLACE OF BIRTH", "MARENHAL")
field2(1, 2, "IZDANO / DATE OF ISSUE", dm(ISSUE))
field2(0, 3, "ORGAN / AUTHORITY", "MARENHAL PASSPORT OFFICE")
field2(1, 3, "VELJA DO / DATE OF EXPIRY", dm(EXPIRY))
# signature
sy = fy + 4 * 38 * S + 6 * S
d.line([(rx0, sy + 22 * S), (rx0 + 200 * S, sy + 22 * S)], fill=ink, width=1)
T(d, (rx0, sy + 26 * S), "PODPIS / HOLDER'S SIGNATURE", fl, lab)
sig = [(0, 14), (8, 2), (14, 18), (22, 4), (30, 16), (40, 8), (52, 14), (66, 3), (80, 12), (100, 8), (120, 14), (140, 6)]
d.line([(rx0 + 10 * S + x * S, sy + (y - 4) * S) for x, y in sig], fill=(30, 40, 110), width=2 * S, joint="curve")

# MRZ
mz = font("consolab.ttf", 34.5 / S * S / S) if False else ImageFont.truetype(os.path.join(F, "consolab.ttf"), 34)
my0 = RP[3] - 62 * S
d.rectangle((RP[0] + 12 * S, my0 - 8 * S, RP[2] - 12 * S, RP[3] - 14 * S), fill=(246, 240, 222))
mw = d.textlength("<" * 44, font=mz)
mxl = (RP[0] + RP[2]) // 2 - mw / 2
T(d, (mxl, my0), l1, mz, (22, 22, 26))
T(d, (mxl, my0 + 22 * S), l2, mz, (22, 22, 26))
assert mw / S / 44 > 9.2, mw / S / 44

# ---------- finishing ----------
# paper grain
grain = Image.frombytes("L", (W, H), rnd.randbytes(W * H)).filter(ImageFilter.GaussianBlur(0.6))
grain = ImageChops.add(Image.new("L", (W, H), 0), grain)
g3 = Image.merge("RGB", (grain, grain, grain))
img = Image.blend(img, ImageChops.overlay(img, g3), 0.10)

# gutter shadow + curvature
sh = Image.new("L", (W, H), 0)
sd = ImageDraw.Draw(sh)
for x in range(W):
    dist = abs(x - mid) / (28 * S)
    v = 0
    if dist < 6:
        v = int(150 * math.exp(-dist * dist * 0.9))
    sd.line([(x, 0), (x, H)], fill=v)
dark = Image.new("RGB", (W, H), (20, 14, 10))
img = Image.composite(dark, img, sh)
d = ImageDraw.Draw(img)
d.line([(mid, M), (mid, H - M)], fill=(120, 108, 92), width=1)

# vignette
vg = Image.new("L", (W, H), 0)
vd = ImageDraw.Draw(vg)
vd.ellipse((-W * 0.15, -H * 0.2, W * 1.15, H * 1.2), fill=255)
vg = vg.filter(ImageFilter.GaussianBlur(120)).point(lambda v: 255 - v)
img = Image.composite(Image.new("RGB", (W, H), (10, 8, 6)), img, vg.point(lambda v: int(v * 0.35)))

out = img.resize((1024, 724), Image.LANCZOS)
out.save("entry.png", optimize=True)
if os.path.getsize("entry.png") > 1_000_000:
    out.save("entry.png", format="JPEG", quality=92)
assert out.size == (1024, 724)
assert os.path.getsize("entry.png") <= 1_000_000
print("OK", os.path.getsize("entry.png"), l1, l2, sep="\n")
