"""Shared look for every chart: colors, fonts, canvas size, and the footer."""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

CLEAN = Path(__file__).resolve().parents[1] / "data" / "clean"

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#8a8984"
GRID = "#e4e3df"

# Party identity uses the conventional hues so readers don't need a key to decode them.
DEM = "#2a78d6"
REP = "#e34948"
OTHER = "#a3a29c"
DEM_LIGHT = "#cde2fb"
REP_LIGHT = "#f8d3d1"
NEUTRAL = "#f0efec"
ACCENT = "#0d366b"

# Diverging: toward Republicans (red) <- gray -> toward Democrats (blue). Equal steps per arm.
SHIFT_CMAP = LinearSegmentedColormap.from_list(
    "shift", ["#8f1d1c", "#e34948", "#f4a8a3", NEUTRAL, "#9ec5f4", "#2a78d6", "#0d366b"])

FIGSIZE = (12, 15)  # 1200 x 1500 px at dpi 100: LinkedIn portrait


def setup() -> None:
    plt.rcParams.update({
        "font.family": "Inter", "font.size": 15, "text.color": INK,
        "axes.edgecolor": GRID, "axes.labelcolor": INK_2,
        "xtick.color": INK_2, "ytick.color": INK_2,
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
        "text.parse_math": False,  # dollar signs are text, not math
    })


def titles(fig, line1: str, line2: str, subtitle: str) -> None:
    fig.text(0.04, 0.955, line1, fontsize=30, weight="bold")
    fig.text(0.04, 0.925, line2, fontsize=30, weight="bold")
    fig.text(0.04, 0.89, subtitle, fontsize=16, color=INK_2, va="top", linespacing=1.4)


def footer(fig, notes: list[str], source: str) -> None:
    y = 0.02 + 0.018 * len(notes)
    for n in notes:
        fig.text(0.04, y, n, fontsize=12.5, color=INK_2)
        y -= 0.018
    fig.text(0.04, 0.02, f"Data: {source}. Chart: Bhrett Boggs", fontsize=12.5, color=MUTED)


def money(v: float) -> str:
    return f"${v / 1e9:.2f}B" if v >= 1e9 else f"${v / 1e6:,.0f}M"
