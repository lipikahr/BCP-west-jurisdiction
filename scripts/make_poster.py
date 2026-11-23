"""Poster PDF of Traffic West stations from the verified dataset."""
from __future__ import annotations

import json
import math
import time
import urllib.request
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Circle, FancyBboxPatch, Polygon
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
STATIONS = json.loads((ROOT / "src" / "data" / "stations.json").read_text(encoding="utf-8"))
TILE_DIR = ROOT / "output" / "tiles"
OUT = ROOT / "output" / "Bengaluru_Traffic_West_Division.pdf"
PREVIEW = ROOT / "output" / "poster_preview.png"

TRAFFIC_NUMBERS = {
    "vyn-tr-magadi": 29,
    "vyn-tr-vijayanagara": 30,
    "vyn-tr-kamakshipalya": 31,
    "vyn-tr-jnanabharathi": 32,
    "pny-tr-malleshwaram": 33,
    "pny-tr-rajajinagar": 34,
    "pny-tr-peenya": 35,
    "pny-tr-sadashivanagar": 36,
    "wst-tr-byatarayanapura": 37,
    "wst-tr-kengeri": 38,
    "wst-tr-girinagar": 39,
}
LAW_NUMBERS = {
    "vyn-lo-kamakshipalya": 1,
    "vyn-lo-kp-agrahara": 2,
    "vyn-lo-magadi": 3,
    "vyn-lo-vijayanagara": 4,
    "vyn-lo-govindarajanagar": 5,
    "pny-lo-malleshwaram": 6,
    "pny-lo-sadashivanagar": 7,
    "pny-lo-srirampura": 8,
    "pny-lo-subramanyanagar": 9,
    "pny-lo-mahalakshmi": 10,
    "pny-lo-rajajinagar": 11,
    "pny-lo-nandini": 12,
    "vyn-lo-basaveshwaranagar": 13,
    "vyn-lo-jnanabharathi": 14,
    "wst-lo-kengeri": 15,
    "wst-lo-kumbalagodu": 16,
    "wst-lo-byatarayanapura": 17,
    "vyn-lo-ap-nagar": 18,
    "wst-lo-chandra": 19,
    "wst-lo-rr-nagar": 20,
    "wst-lo-ck-achukattu": 21,
    "wst-lo-girinagar": 22,
    "wst-lo-hanumanthanagar": 23,
    "wst-lo-kg-nagar": 24,
    "vyn-lo-byadarahalli": 25,
    "pny-lo-peenya": 26,
    "pny-lo-rajagopalanagar": 27,
    "pny-lo-madanayakanahalli": 28,
}
ACP_ORDER = [
    "ACP Traffic – Vijayanagara",
    "ACP Traffic – Peenya",
    "ACP Traffic – West",
]
ACP_SHORT = {
    "ACP Traffic – Vijayanagara": "Vijayanagara",
    "ACP Traffic – Peenya": "Peenya",
    "ACP Traffic – West": "West",
}
UA = "TrafficWestDivisionPoster/1.0 (academic map; local)"


def hull(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    pts = sorted(set(points), key=lambda p: (p[1], p[0]))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[1] - o[1]) * (b[0] - o[0]) - (a[0] - o[0]) * (b[1] - o[1])

    lower: list[tuple[float, float]] = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper: list[tuple[float, float]] = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def expand(ring: list[tuple[float, float]], factor: float) -> list[tuple[float, float]]:
    if len(ring) < 3:
        return ring
    lat = sum(p[0] for p in ring) / len(ring)
    lon = sum(p[1] for p in ring) / len(ring)
    return [(lat + (y - lat) * factor, lon + (x - lon) * factor) for y, x in ring]


def tile_xy(lat: float, lon: float, zoom: int) -> tuple[int, int]:
    n = 2**zoom
    x = int((lon + 180) / 360 * n)
    lat_r = math.radians(lat)
    y = int((1 - math.log(math.tan(lat_r) + 1 / math.cos(lat_r)) / math.pi) / 2 * n)
    return x, y


def tile_bounds(x: int, y: int, zoom: int) -> tuple[float, float, float, float]:
    n = 2**zoom
    west = x / n * 360 - 180
    east = (x + 1) / n * 360 - 180

    def lat_of(row: int) -> float:
        return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * row / n))))

    north = lat_of(y)
    south = lat_of(y + 1)
    return west, south, east, north


def fetch_basemap(south: float, west: float, north: float, east: float, zoom: int = 13) -> tuple[Image.Image, tuple[float, float, float, float]]:
    x0, y_north = tile_xy(north, west, zoom)
    x1, y_south = tile_xy(south, east, zoom)
    xs = range(min(x0, x1), max(x0, x1) + 1)
    ys = range(min(y_north, y_south), max(y_north, y_south) + 1)
    tiles = {}
    for x in xs:
        for y in ys:
            path = TILE_DIR / str(zoom) / str(x) / f"{y}.png"
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                url = f"https://tile.openstreetmap.org/{zoom}/{x}/{y}.png"
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=30) as response:
                    path.write_bytes(response.read())
                time.sleep(0.12)
            tiles[(x, y)] = Image.open(path).convert("RGB")
    width = len(list(xs)) * 256
    height = len(list(ys)) * 256
    canvas = Image.new("RGB", (width, height))
    for ix, x in enumerate(xs):
        for iy, y in enumerate(ys):
            canvas.paste(tiles[(x, y)], (ix * 256, iy * 256))
    west_b, _, _, north_b = tile_bounds(min(xs), min(ys), zoom)
    _, south_b, east_b, _ = tile_bounds(max(xs), max(ys), zoom)
    return canvas, (west_b, east_b, south_b, north_b)


def plotted(kind: str) -> list[dict]:
    numbers = TRAFFIC_NUMBERS if kind == "traffic" else LAW_NUMBERS
    rows = []
    for station in STATIONS:
        if station["type"] != kind:
            continue
        station = dict(station)
        station["number"] = numbers[station["id"]]
        rows.append(station)
    return sorted(rows, key=lambda row: row["number"])


def km_between(a: dict, b: dict) -> float:
    dlat = (a["latitude"] - b["latitude"]) * 111
    dlon = (a["longitude"] - b["longitude"]) * 111 * math.cos(math.radians(a["latitude"]))
    return math.hypot(dlat, dlon)


def place_callout_labels(ax, items: list[dict]) -> None:
    located = [station for station in items if station["latitude"] is not None]
    clustered: set[int] = set()
    for i, left in enumerate(located):
        for j in range(i + 1, len(located)):
            if km_between(left, located[j]) < 3.8:
                clustered.add(i)
                clustered.add(j)
    isolated = [station for index, station in enumerate(located) if index not in clustered]
    crowd = [station for index, station in enumerate(located) if index in clustered]
    for index, station in enumerate(isolated):
        angle = (index / max(len(isolated), 1)) * math.tau
        ax.annotate(
            station["short_name"],
            xy=(station["longitude"], station["latitude"]),
            xytext=(math.cos(angle) * 16, math.sin(angle) * 12),
            textcoords="offset points",
            fontsize=7,
            fontweight="semibold",
            color="#1c2430",
            ha="center",
            va="center",
            arrowprops={"arrowstyle": "-", "color": "#334155", "lw": 0.55},
            bbox={"boxstyle": "round,pad=0.16", "fc": "white", "ec": "#94a3b8", "lw": 0.4, "alpha": 0.96},
            zorder=6,
        )
    if not crowd:
        return
    median = sorted(station["longitude"] for station in crowd)[len(crowd) // 2]
    west_edge, east_edge = ax.get_xlim()
    south_edge, north_edge = ax.get_ylim()
    span = north_edge - south_edge
    for side, group in (
        ("left", sorted((station for station in crowd if station["longitude"] <= median), key=lambda row: row["latitude"])),
        ("right", sorted((station for station in crowd if station["longitude"] > median), key=lambda row: row["latitude"])),
    ):
        if not group:
            continue
        slot = span * 0.72 / max(len(group) - 1, 1)
        base = south_edge + span * 0.14
        label_lon = west_edge + (east_edge - west_edge) * (0.04 if side == "left" else 0.96)
        for index, station in enumerate(group):
            ax.annotate(
                f"{station['number']}  {station['short_name']}",
                xy=(station["longitude"], station["latitude"]),
                xytext=(label_lon, base + index * slot),
                textcoords="data",
                fontsize=6.4,
                fontweight="semibold",
                color="#1c2430",
                ha="left" if side == "left" else "right",
                va="center",
                arrowprops={"arrowstyle": "-", "color": "#475569", "lw": 0.45, "shrinkA": 0, "shrinkB": 2},
                bbox={"boxstyle": "round,pad=0.14", "fc": "white", "ec": "#94a3b8", "lw": 0.35, "alpha": 0.96},
                zorder=6,
            )


def spread_labels(ax, items: list[dict]) -> None:
    located = [station for station in items if station["latitude"] is not None]
    anns = []
    for index, station in enumerate(located):
        angle = (index / max(len(located), 1)) * math.tau
        anns.append(
            ax.annotate(
                station["short_name"],
                xy=(station["longitude"], station["latitude"]),
                xytext=(math.cos(angle) * 22, math.sin(angle) * 16),
                textcoords="offset points",
                fontsize=6.6,
                fontweight="semibold",
                color="#1c2430",
                ha="center",
                va="center",
                arrowprops={"arrowstyle": "-", "color": "#334155", "lw": 0.55},
                bbox={"boxstyle": "round,pad=0.16", "fc": "white", "ec": "#94a3b8", "lw": 0.4, "alpha": 0.96},
                zorder=6,
            )
        )
    fig = ax.figure
    scale = fig.dpi / 72
    for _ in range(80):
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        boxes = [ann.get_window_extent(renderer).expanded(1.12, 1.45) for ann in anns]
        moved = False
        for i, box in enumerate(boxes):
            shift = np.zeros(2)
            for j, other in enumerate(boxes):
                if i == j or not box.overlaps(other):
                    continue
                center = np.array([box.x0 + box.width / 2, box.y0 + box.height / 2])
                other_center = np.array([other.x0 + other.width / 2, other.y0 + other.height / 2])
                delta = center - other_center
                norm = np.linalg.norm(delta)
                if norm < 1:
                    delta = np.array([1.0, 0.4])
                    norm = np.linalg.norm(delta)
                shift += delta / norm * 14
            if np.linalg.norm(shift) > 0.4:
                x, y = anns[i].xyann
                anns[i].set_position((x + shift[0] / scale, y + shift[1] / scale))
                moved = True
        if not moved:
            break


def draw_page(pdf, kind: str, title: str, subtitle: str, note: str) -> None:
    rows = plotted(kind)
    located = [row for row in rows if row["latitude"] is not None]
    lats = [row["latitude"] for row in located]
    lons = [row["longitude"] for row in located]
    pad_lat, pad_lon = 0.035, 0.045
    image, (west, east, south, north) = fetch_basemap(
        min(lats) - pad_lat, min(lons) - pad_lon, max(lats) + pad_lat, max(lons) + pad_lon
    )

    fig = plt.figure(figsize=(16.54, 11.69), dpi=140)
    fig.patch.set_facecolor("#f4f7fb")
    header = fig.add_axes([0, 0.9, 1, 0.1])
    header.set_axis_off()
    header.set_xlim(0, 1)
    header.set_ylim(0, 1)
    header.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="square,pad=0", fc="#10233f", ec="none", transform=header.transAxes))
    header.text(0.5, 0.66, "BENGALURU TRAFFIC WEST DIVISION", ha="center", va="center", color="white", fontsize=22, fontweight="bold")
    header.text(0.5, 0.28, subtitle, ha="center", va="center", color="#fbbf24", fontsize=12, fontweight="medium")

    side = fig.add_axes([0.015, 0.045, 0.25, 0.84])
    side.set_axis_off()
    side.set_xlim(0, 1)
    side.set_ylim(0, 1)
    side.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.008,rounding_size=0.02", fc="white", ec="#d5deea", lw=0.8, transform=side.transAxes))
    side.text(0.06, 0.965, title, fontsize=10.5, fontweight="bold", color="#10233f", va="top")
    y = 0.93
    for acp in ACP_ORDER:
        group = [row for row in rows if row["acp"] == acp]
        if not group:
            continue
        colour = group[0]["acp_colour"]
        side.add_patch(FancyBboxPatch((0.05, y - 0.028), 0.9, 0.034, boxstyle="round,pad=0.002,rounding_size=0.008", fc=colour, ec="none", transform=side.transAxes))
        side.text(0.08, y - 0.011, f"{ACP_SHORT[acp]}  ·  {len(group)} stations", color="white", fontsize=8, fontweight="bold", va="center")
        y -= 0.04
        for row in group:
            missing = row["latitude"] is None
            side.text(0.08, y, f"{row['number']:>2}", color=colour, fontsize=8, fontweight="bold", va="center")
            label = row["name"].replace(" Police Station", "")
            if missing:
                label += "  (not plotted)"
            side.text(0.16, y, label, color="#334155" if missing else "#1c2430", fontsize=7.3, va="center")
            y -= 0.028
        y -= 0.012

    ax = fig.add_axes([0.28, 0.08, 0.7, 0.8])
    ax.imshow(np.asarray(image), extent=(west, east, south, north), origin="upper", zorder=0, interpolation="bilinear")
    ax.set_xlim(min(lons) - pad_lon * 0.7, max(lons) + pad_lon * 0.7)
    ax.set_ylim(min(lats) - pad_lat * 0.55, max(lats) + pad_lat * 0.55)
    ax.set_axis_off()

    for acp in ACP_ORDER:
        members = [row for row in STATIONS if row["acp"] == acp and row["latitude"] is not None]
        if kind == "law_and_order":
            members = [row for row in members if row["type"] == "law_and_order"]
        ring = expand(hull([(row["latitude"], row["longitude"]) for row in members]), 1.22)
        if len(ring) < 3:
            continue
        colour = members[0]["acp_colour"]
        ax.add_patch(Polygon([(lon, lat) for lat, lon in ring], closed=True, fc=colour, ec=colour, alpha=0.18, lw=1.6, zorder=2))

    for row in located:
        ax.add_patch(Circle((row["longitude"], row["latitude"]), 0.0042, fc=row["acp_colour"], ec="white", lw=1.1, zorder=5))
        ax.text(row["longitude"], row["latitude"], str(row["number"]), color="white", fontsize=6.2, fontweight="bold", ha="center", va="center", zorder=6)
    if kind == "law_and_order":
        place_callout_labels(ax, located)
    else:
        spread_labels(ax, located)

    ax.text(
        0.01,
        0.01,
        "Map data © OpenStreetMap contributors   ·   Station pins from Google Maps place coordinates\n"
        + note,
        transform=ax.transAxes,
        fontsize=6.4,
        color="#1c2430",
        va="bottom",
        bbox={"boxstyle": "round,pad=0.35", "fc": "white", "ec": "#d5deea", "alpha": 0.94},
    )

    legend = fig.add_axes([0.3, 0.012, 0.66, 0.055])
    legend.set_axis_off()
    legend.set_xlim(0, 1)
    legend.set_ylim(0, 1)
    x = 0.01
    for acp in ACP_ORDER:
        colour = next(row["acp_colour"] for row in STATIONS if row["acp"] == acp)
        legend.add_patch(FancyBboxPatch((x, 0.25), 0.035, 0.5, boxstyle="round,pad=0.002,rounding_size=0.01", fc=colour, ec="none"))
        legend.text(x + 0.045, 0.5, ACP_SHORT[acp], va="center", fontsize=8, color="#1c2430")
        x += 0.16
    legend.text(x, 0.5, "Numbered pin = station    ·    Shading groups plotted stations, not an official boundary", va="center", fontsize=7.4, color="#334155")
    pdf.savefig(fig)
    fig.savefig(PREVIEW.parent / f"poster_preview_{kind}.png")
    plt.close(fig)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(OUT) as pdf:
        draw_page(
            pdf,
            "traffic",
            "Traffic police stations",
            "Traffic Police Stations  ·  11 stations  ·  numbers 29–39",
            "Shaded areas are drawn from verified station coordinates. They are not an official jurisdiction boundary.\n"
            "Girinagar Traffic (39) is listed and not plotted: no verified coordinate.",
        )
        draw_page(
            pdf,
            "law_and_order",
            "Law & order police stations",
            "Law & Order Police Stations  ·  28 stations  ·  numbers 1–28",
            "Colour follows the Traffic ACP grouping in the source document.\n"
            "Shaded areas are drawn from verified station coordinates. They are not an official jurisdiction boundary.",
        )
    print(OUT)


if __name__ == "__main__":
    main()
