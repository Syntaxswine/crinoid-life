# Hold On

*the life of a crinoid, in ten seasons or fewer*

**Play:** https://syntaxswine.github.io/crinoid-life/

A short choose-your-own-adventure. You are a crinoid — a sea lily, which is an
animal, a cousin of the starfish, built from a few thousand plates of calcite.
Choose an era (the Carboniferous meadow, or the present-day deep), find
something hard to hold on to as a larva, and live ten seasons of feeding,
storms, urchins, fish, and tenants. Eleven endings, remembered in your browser.

Same voice as [Twenty-One Pages](https://syntaxswine.github.io/cheesecake-cyoa/):
deadpan, second person, and every fact is real.

<p align="center"><img src="qr-crinoid.png" width="360" alt="A QR code for this repo, drawn as a crinoid: the code is the crown, ten arms fan up through it, and a stalk of columnals runs down to a holdfast."></p>

The QR code above scans to this repo. It is a sea lily: ten arms rise from
the cup and pass *through* the code as a tint that keeps every module's
light/dark value (dark modules turn deep rose, light modules pale rose), so
the bits are unchanged; version 5, error correction H. `tools/make_qr.py`
rebuilds it and refuses to write a pass unless two independent decoders
read it back: ZXing at every size down to 3px/module, blurred, and in
greyscale; OpenCV at 4–10px/module. A plain code is decoded first as the
control. Under simulated phone capture (tilt, perspective, dim exposure,
JPEG q40) ZXing read it 40/40.

## Files

- `index.html` — the whole game, one self-contained file, no build.
- `qr-crinoid.svg` / `qr-crinoid.png` — the QR code (SVG for print, PNG at 20px/module).
- `tools/make_qr.py` — builds and decode-checks it (`pip install segno pillow opencv-python-headless zxing-cpp`).

## The facts

Real: mouth and anus both on the upper surface; non-feeding yolky larvae;
stalked crinoids crawling away from cidaroid urchins; platyceratid snails
fossilised in place on crinoid anal vents; each plate a single calcite crystal;
crinoidal limestone (the Burlington, across Missouri, Iowa and Illinois);
Crawfordsville, Indiana; St Cuthbert's beads on Lindisfarne; the crinoid as
Missouri's state fossil (1989); feather stars as most of the living species.

Compressed for play: season lengths, odds, and the choice of era. No crinoid
gets to choose its geological period.

## Balance

Measured by bot play: careful present-day play starves ~4% of the time;
the "cup on a stick" ending needs reckless play. All eleven endings are
reachable.
