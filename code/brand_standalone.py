"""Carbon-Drawdown logo branding for matplotlib figures — self-contained drop-in.

Ship this file together with `logo_brand.png` (a 360x199 RGBA PNG whose white card is
already keyed transparent). Point LOGO_PATH at that file.

Usage — one figure at a time:
    import brand_standalone as brand
    fig, ax = plt.subplots(...); ...
    fig.tight_layout()          # layout FIRST
    brand.add_logo(fig)         # then the logo (AFTER tight_layout)
    fig.savefig("out.png", dpi=150)

Usage — brand EVERY save automatically (call once at program start):
    import brand_standalone as brand
    brand.enable_autobrand()    # now every fig.savefig / plt.savefig is stamped

Requires: matplotlib, pillow, numpy.
"""
from __future__ import annotations
import os

# --- point this at the logo PNG (same folder by default) ---
LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_brand.png")

_img = None  # loaded once


def _load():
    global _img
    if _img is None:
        from PIL import Image
        import numpy as np
        _img = np.asarray(Image.open(LOGO_PATH).convert("RGBA"))
    return _img


def add_logo(fig, ax=None, frac=0.14, pad=0.018, loc="lower right", alpha=0.9):
    """Overlay the logo as a small watermark INSIDE the chart area, aspect preserved.

    frac = logo width as a fraction of the axes width; loc in {lower/upper}x{right/left}
    (pick an empty corner). Never raises — branding must not break a figure.
    """
    try:
        img = _load()
    except Exception:
        return None
    lh, lw = img.shape[:2]
    fw_in, fh_in = fig.get_size_inches()
    if ax is None and fig.axes:
        ax = max(fig.axes, key=lambda a: (a.get_position().width * a.get_position().height))
    box = ax.get_position() if ax is not None else fig.bbox_inches
    bx, by, bw, bh = box.x0, box.y0, box.width, box.height
    w = frac * bw
    h = w * (fw_in / fh_in) * (lh / lw)          # preserve pixel aspect ratio
    x = (bx + bw - w - pad * bw) if "right" in loc else (bx + pad * bw)
    y = (by + bh - h - pad * bh) if "upper" in loc else (by + pad * bh)
    logo = fig.add_axes([x, y, w, h], zorder=10_000)
    logo.imshow(img, alpha=alpha, interpolation="lanczos")
    logo.axis("off")
    logo.set_facecolor("none")
    return logo


def enable_autobrand(**logo_kw):
    """Monkeypatch matplotlib so EVERY figure save is branded. Call ONCE. Idempotent
    per-figure; covers fig.savefig and plt.savefig; never raises."""
    from matplotlib.figure import Figure
    if getattr(Figure, "_autobrand_on", False):
        return False
    _orig = Figure.savefig

    def _branded(self, *a, **k):
        try:
            if not getattr(self, "_branded", False) and self.get_axes():
                add_logo(self, **logo_kw)
                self._branded = True
        except Exception:
            pass
        return _orig(self, *a, **k)

    Figure.savefig = _branded
    Figure._autobrand_on = True
    return True


if __name__ == "__main__":
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    enable_autobrand()
    fig, ax = plt.subplots(figsize=(8, 5)); ax.plot([0, 1, 2], [0, 1, 0.5])
    ax.set_title("autobrand test"); fig.tight_layout()
    fig.savefig("brand_test.png", dpi=150)
    print("wrote brand_test.png")
