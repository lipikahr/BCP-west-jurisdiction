"""Poster pair matching the Traffic West reference design, with verified coordinates."""
from __future__ import annotations

import json
import math
import time
import urllib.request
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patheffects as pe
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle, Wedge
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
REF = Path(
    r"C:\Users\lipik\.cursor\projects\c-Projects-TrafficWest\assets"
    r"\WhatsApp_Image_2026-11-23_at_23.21.13-58efde95-dc72-4a5d-a4dc-a35f473da396.jpg"
)
STATIONS = json.loads((ROOT / "src" / "data" / "stations.json").read_text(encoding="utf-8"))
TILE_DIR = ROOT / "output" / "tiles_esri"
ROADS = ROOT / "output" / "major_roads.json"
OUT = ROOT / "output" / "Bengaluru_Traffic_West_Division.pdf"
UA = "TrafficWestDivisionPoster/1.0 (local map)"

SOUTH, WEST, NORTH, EAST = 12.835, 77.40, 13.105, 77.625
NAVY = "#071e57"
YELLOW = "#ffe500"
PIN_RED = (214, 28, 36, 255)
ROAD_YELLOW = "#f5c400"
ROAD_WHITE = "#fff7cc"
ROAD_GRAY = "#c5c8ce"

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

GROUPS = [
    {
        "acp": "ACP Traffic – Vijayanagara",
        "name": "Vijayanagar",
        "header": "#6d4ea3",
        "fill": "#d7c2f2",
        "soft": "#efe4fb",
    },
    {
        "acp": "ACP Traffic – Peenya",
        "name": "Peenya",
        "header": "#2f74c0",
        "fill": "#b7daf8",
        "soft": "#e5f3fd",
    },
    {
        "acp": "ACP Traffic – West",
        "name": "West",
        "header": "#3e9a45",
        "fill": "#c8efbf",
        "soft": "#e7f8e3",
    },
]

plt.rcParams["font.family"] = "Arial"


def km(a_lat: float, a_lon: float, b_lat: float, b_lon: float) -> float:
    dlat = (a_lat - b_lat) * 110.574
    dlon = (a_lon - b_lon) * 111.320 * math.cos(math.radians((a_lat + b_lat) / 2))
    return math.hypot(dlat, dlon)


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

    return west, lat_of(y + 1), east, lat_of(y)


def fetch_basemap(zoom: int = 13):
    x0, y_north = tile_xy(NORTH, WEST, zoom)
    x1, y_south = tile_xy(SOUTH, EAST, zoom)
    xs = range(min(x0, x1), max(x0, x1) + 1)
    ys = range(min(y_north, y_south), max(y_north, y_south) + 1)
    tiles = {}
    for x in xs:
        for y in ys:
            path = TILE_DIR / str(zoom) / str(x) / f"{y}.png"
            if not path.exists() or path.stat().st_size < 500:
                path.parent.mkdir(parents=True, exist_ok=True)
                url = f"https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{zoom}/{y}/{x}"
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=40) as response:
                    path.write_bytes(response.read())
                time.sleep(0.05)
            tiles[(x, y)] = Image.open(path).convert("RGB")
    sample = next(iter(tiles.values()))
    canvas = Image.new("RGB", (len(list(xs)) * sample.width, len(list(ys)) * sample.height), (245, 243, 236))
    for ix, x in enumerate(xs):
        for iy, y in enumerate(ys):
            canvas.paste(tiles[(x, y)], (ix * sample.width, iy * sample.height))
    paper = Image.new("RGB", canvas.size, (252, 250, 246))
    canvas = Image.blend(canvas, paper, 0.08)
    west_b, _, _, north_b = tile_bounds(min(xs), min(ys), zoom)
    _, south_b, east_b, _ = tile_bounds(max(xs), max(ys), zoom)
    return canvas, (west_b, east_b, south_b, north_b)


def fetch_roads() -> list[dict]:
    if ROADS.exists() and ROADS.stat().st_size > 1000:
        return json.loads(ROADS.read_text(encoding="utf-8"))
    query = f"""
    [out:json][timeout:120];
    way["highway"~"motorway|trunk|primary|secondary"]({SOUTH},{WEST},{NORTH},{EAST});
    out geom;
    """
    last_error = None
    for endpoint in (
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
    ):
        try:
            req = urllib.request.Request(
                endpoint,
                data=query.encode("utf-8"),
                headers={"User-Agent": UA, "Content-Type": "text/plain"},
            )
            with urllib.request.urlopen(req, timeout=150) as response:
                payload = json.loads(response.read().decode("utf-8"))
            ways = []
            for element in payload.get("elements", []):
                if element.get("type") != "way" or "geometry" not in element:
                    continue
                tags = element.get("tags", {})
                ways.append(
                    {
                        "highway": tags.get("highway", ""),
                        "name": tags.get("name", ""),
                        "ref": tags.get("ref", ""),
                        "coords": [[point["lat"], point["lon"]] for point in element["geometry"]],
                    }
                )
            ROADS.write_text(json.dumps(ways), encoding="utf-8")
            return ways
        except Exception as error:  # noqa: BLE001 - try the next Overpass server
            last_error = error
    raise RuntimeError(f"Could not download roads: {last_error}")


def blur(values: np.ndarray, passes: int) -> np.ndarray:
    out = values.astype(float)
    for _ in range(passes):
        padded = np.pad(out, 1, mode="edge")
        out = (
            padded[:-2, 1:-1]
            + padded[2:, 1:-1]
            + padded[1:-1, :-2]
            + padded[1:-1, 2:]
            + padded[1:-1, 1:-1] * 2
        ) / 6
    return out


def region_field():
    points = []
    for index, group in enumerate(GROUPS):
        for station in STATIONS:
            if station["acp"] == group["acp"] and station["latitude"] is not None:
                points.append((station["latitude"], station["longitude"], index))
    lats = np.linspace(SOUTH, NORTH, 340)
    lons = np.linspace(WEST, EAST, 380)
    lon_grid, lat_grid = np.meshgrid(lons, lats)
    nearest = np.full(lat_grid.shape, 1e9)
    owner = np.zeros(lat_grid.shape)
    for lat, lon, index in points:
        dlat = (lat_grid - lat) * 110.574
        dlon = (lon_grid - lon) * 111.320 * math.cos(math.radians(lat))
        distance = np.hypot(dlat, dlon)
        closer = distance < nearest
        nearest = np.where(closer, distance, nearest)
        owner = np.where(closer, index, owner)
    # Connect stations of the same subdivision so the area is one shape, not scattered dots.
    link = np.full(lat_grid.shape, 1e9)
    for index, group in enumerate(GROUPS):
        members = [(lat, lon) for lat, lon, owner_index in points if owner_index == index]
        if len(members) < 2:
            continue
        remaining = set(range(1, len(members)))
        connected = {0}
        while remaining:
            best = None
            for left in connected:
                for right in remaining:
                    distance = km(members[left][0], members[left][1], members[right][0], members[right][1])
                    if best is None or distance < best[0]:
                        best = (distance, left, right)
            start, end = members[best[1]], members[best[2]]
            steps = max(int(best[0] / 0.55), 1)
            for step in range(steps + 1):
                share = step / steps
                lat = start[0] + (end[0] - start[0]) * share
                lon = start[1] + (end[1] - start[1]) * share
                dlat = (lat_grid - lat) * 110.574
                dlon = (lon_grid - lon) * 111.320 * math.cos(math.radians(lat))
                distance = np.hypot(dlat, dlon)
                link = np.minimum(link, distance)
            connected.add(best[2])
            remaining.remove(best[2])
    inside = (nearest <= 3.15) | (link <= 1.55)
    smooth = blur(inside.astype(float), 7)
    scores = [blur(((owner == index) & inside).astype(float), 5) for index in range(3)]
    stacked = np.stack(scores)
    winner = stacked.argmax(axis=0).astype(float)
    strength = stacked.max(axis=0)
    field = np.ma.masked_where((smooth < 0.42) | (strength < 0.18), winner)
    return lon_grid, lat_grid, field, smooth


def pin_image(number: int, kind: str) -> np.ndarray:
    width, height = 150, 196
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((18, 14, 132, 128), fill=PIN_RED)
    draw.polygon([(75, 184), (28, 86), (122, 86)], fill=PIN_RED)
    draw.ellipse((36, 32, 114, 110), fill=(255, 255, 255, 255))
    font = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 34 if number < 10 else 30)
    text = str(number)
    box = draw.textbbox((0, 0), text, font=font)
    draw.text(((width - (box[2] - box[0])) / 2, 40), text, fill=(176, 18, 28, 255), font=font)
    if kind == "traffic":
        draw.rounded_rectangle((52, 78, 98, 96), radius=4, fill=(25, 92, 176, 255))
        draw.polygon([(58, 80), (68, 70), (86, 70), (94, 80)], fill=(25, 92, 176, 255))
        draw.ellipse((58, 90, 70, 102), fill=(35, 35, 35, 255))
        draw.ellipse((82, 90, 94, 102), fill=(35, 35, 35, 255))
    else:
        draw.polygon([(60, 86), (75, 74), (90, 86)], fill=(25, 92, 176, 255))
        draw.rectangle((62, 86, 88, 104), fill=(25, 92, 176, 255))
        draw.rectangle((70, 92, 80, 104), fill=(255, 255, 255, 255))
    return np.asarray(image)


def halo(size: float = 3.2):
    return [pe.withStroke(linewidth=size, foreground="white")]


def draw_header(fig, yellow: str, banner: str) -> None:
    header = fig.add_axes([0, 0.862, 1, 0.138])
    header.set_xlim(0, 1)
    header.set_ylim(0, 1)
    header.set_axis_off()
    header.add_patch(Rectangle((0, 0), 1, 1, fc=NAVY, ec="none"))
    ref = Image.open(REF).convert("RGBA")
    logo = ref.crop((72, 0, 250, 92))
    building = ref.crop((800, 0, 1024, 90))
    logo_ax = fig.add_axes([0.008, 0.872, 0.112, 0.118])
    logo_ax.imshow(np.asarray(logo), aspect="auto")
    logo_ax.set_axis_off()
    building_ax = fig.add_axes([0.785, 0.874, 0.205, 0.114])
    building_ax.imshow(np.asarray(building), aspect="auto")
    building_ax.set_axis_off()
    header.text(0.46, 0.80, "BENGALURU WEST COMMISSIONERATE", ha="center", va="center", color="white", fontsize=15, fontweight="bold")
    header.text(0.46, 0.50, yellow, ha="center", va="center", color=YELLOW, fontsize=26, fontweight="bold", fontname="Impact")
    header.add_patch(FancyBboxPatch((0.24, 0.08), 0.44, 0.22, boxstyle="round,pad=0.005,rounding_size=0.12", fc="#e10600", ec="none"))
    header.text(0.46, 0.19, banner, ha="center", va="center", color="white", fontsize=10.5, fontweight="bold")


def draw_sidebar(fig, kind: str, rows: list[dict]) -> None:
    side = fig.add_axes([0.008, 0.018, 0.228, 0.832])
    side.set_xlim(0, 1)
    side.set_ylim(0, 1)
    side.set_axis_off()
    side.add_patch(FancyBboxPatch((0.01, 0.0), 0.98, 1, boxstyle="round,pad=0.006,rounding_size=0.012", fc="white", ec="#d5d8e0", lw=0.6))
    title = "Traffic West Division\n(11 Traffic Police Stations)" if kind == "traffic" else "West Division\n(28 Law & Order Police Stations)"
    side.add_patch(FancyBboxPatch((0.05, 0.915), 0.90, 0.072, boxstyle="round,pad=0.004,rounding_size=0.03", fc="#123a86", ec="none"))
    side.text(0.50, 0.951, title, ha="center", va="center", color="white", fontsize=8.2, fontweight="bold", linespacing=1.15)
    y = 0.900
    row_h = 0.0245 if kind == "traffic" else 0.0205
    for group in GROUPS:
        members = [row for row in rows if row["acp"] == group["acp"]]
        head = 0.048 if kind == "traffic" else 0.040
        side.add_patch(FancyBboxPatch((0.05, y - head), 0.90, head, boxstyle="round,pad=0.002,rounding_size=0.012", fc=group["header"], ec="none"))
        count = len(members)
        label = f"ACP Traffic {group['name']}\nSubdivision ({count} Stations)"
        side.text(0.50, y - head / 2, label, ha="center", va="center", color="white", fontsize=7.2, fontweight="bold", linespacing=1.05)
        y -= head + 0.006
        body = row_h * len(members) + 0.008
        side.add_patch(FancyBboxPatch((0.05, y - body), 0.90, body, boxstyle="round,pad=0.002,rounding_size=0.01", fc=group["soft"], ec=group["header"], lw=0.4))
        for row in members:
            y -= row_h
            side.text(
                0.11,
                y,
                str(row["number"]),
                ha="center",
                va="center",
                fontsize=6.3,
                fontweight="bold",
                color="#1a1a1a",
                bbox={"boxstyle": "circle,pad=0.16", "fc": YELLOW, "ec": "#c6a400", "lw": 0.3},
                zorder=3,
            )
            name = row["list_name"]
            if row["id"] == "wst-tr-girinagar":
                name = "Girinagar Traffic PS *"
            side.text(0.17, y, name, ha="left", va="center", fontsize=6.5 if kind == "traffic" else 6.0, color="#1c1c1c")
        y -= 0.014
    if kind == "traffic":
        side.text(0.08, 0.078, "* 39 is not pinned. Its location is not verified.", ha="left", va="center", fontsize=5.6, color="#555555", style="italic")
    draw_scale(side)


def draw_scale(side) -> None:
    x0, width, y = 0.10, 0.76, 0.028
    for index in range(4):
        side.add_patch(Rectangle((x0 + index * width / 4, y), width / 4, 0.014, fc="black" if index % 2 == 0 else "white", ec="black", lw=0.6))
    for index, label in enumerate(["0", "2.5", "5", "7.5", "10 km"]):
        side.text(x0 + index * width / 4, y + 0.020, label, ha="center", va="bottom", fontsize=6, color="#222222")


def draw_roads(ax, roads: list[dict]) -> None:
    for way in sorted(roads, key=lambda item: {"secondary": 0, "primary": 1, "trunk": 2, "motorway": 3}.get(item["highway"].replace("_link", ""), 0)):
        highway = way["highway"].replace("_link", "")
        if highway not in {"secondary", "primary", "trunk", "motorway"} or len(way["coords"]) < 2:
            continue
        lats = [point[0] for point in way["coords"]]
        lons = [point[1] for point in way["coords"]]
        if highway == "secondary":
            continue
        if highway == "primary":
            ax.plot(lons, lats, color="#ffe27a", lw=1.55, solid_capstyle="round", zorder=4)
        else:
            ax.plot(lons, lats, color="white", lw=3.6, solid_capstyle="round", zorder=4)
            ax.plot(lons, lats, color=ROAD_YELLOW, lw=2.15, solid_capstyle="round", zorder=5)
    labeled = set()
    wanted = (
        ("tumakuru", "Tumakuru Road (NH 48)"),
        ("tumkur", "Tumakuru Road (NH 48)"),
        ("outer ring", "Outer Ring Road"),
        ("mysuru", "Mysuru Road (NH 275)"),
        ("mysore", "Mysuru Road (NH 275)"),
        ("magadi", "Magadi Road"),
    )
    for way in roads:
        name = (way["name"] or "").lower()
        if way["highway"] not in {"motorway", "trunk", "primary", "trunk_link", "motorway_link"}:
            continue
        for key, label in wanted:
            if key not in name or label in labeled or len(way["coords"]) < 5:
                continue
            mid = way["coords"][len(way["coords"]) // 2]
            if any(km(mid[0], mid[1], station["latitude"], station["longitude"]) < 2.2 for station in STATIONS if station["latitude"] is not None):
                continue
            if any(km(mid[0], mid[1], lat, lon) < 2.4 for lon, lat in ((77.472, 12.972), (77.50, 13.07), (77.50, 12.90))):
                continue
            ax.text(mid[1], mid[0], label, fontsize=6.2, color="#6a5a10", ha="center", va="center", fontstyle="italic", path_effects=halo(2.4), zorder=6)
            labeled.add(label)
            break


def draw_compass(fig) -> None:
    compass = fig.add_axes([0.905, 0.755, 0.055, 0.082])
    compass.set_xlim(-1.2, 1.2)
    compass.set_ylim(-1.35, 1.45)
    compass.set_aspect("equal")
    compass.set_axis_off()
    compass.add_patch(Circle((0, 0), 1.0, fc="white", ec="#222222", lw=0.7, zorder=2))
    compass.add_patch(Polygon([(0, 0.92), (-0.28, 0), (0, 0.16)], closed=True, fc="black", ec="black", lw=0.2, zorder=3))
    compass.add_patch(Polygon([(0, 0.92), (0.28, 0), (0, 0.16)], closed=True, fc="#4b5563", ec="black", lw=0.2, zorder=3))
    compass.add_patch(Polygon([(0, -0.92), (-0.28, 0), (0, -0.16)], closed=True, fc="white", ec="black", lw=0.3, zorder=3))
    compass.add_patch(Polygon([(0, -0.92), (0.28, 0), (0, -0.16)], closed=True, fc="#e5e7eb", ec="black", lw=0.3, zorder=3))
    compass.text(0, 1.22, "N", ha="center", va="center", fontsize=9, fontweight="bold", zorder=4)


def draw_legend(ax, kind: str) -> None:
    ax.add_patch(FancyBboxPatch((0.625, 0.018), 0.358, 0.30, boxstyle="round,pad=0.006,rounding_size=0.012", fc="white", ec="#9aa3b2", lw=0.7, transform=ax.transAxes, zorder=8))
    ax.text(0.804, 0.292, "Legend", transform=ax.transAxes, ha="center", va="center", fontsize=8, fontweight="bold", zorder=9)
    pin_name = "Traffic Police Station (with Station No.)" if kind == "traffic" else "Law & Order Police Station (with Station No.)"
    ranges = (
        ("Vijayanagar Subdivision Jurisdiction (29 – 32)", "#d7c2f2", "#6d4ea3")
        if kind == "traffic"
        else ("Vijayanagar Subdivision (stations in this ACP)", "#d7c2f2", "#6d4ea3")
    )
    items = [
        ("pin", pin_name),
        ("swatch", ranges if kind == "traffic" else ("Vijayanagar Subdivision", "#d7c2f2", "#6d4ea3")),
        ("swatch", ("Peenya Subdivision Jurisdiction (33 – 36)", "#b7daf8", "#2f74c0") if kind == "traffic" else ("Peenya Subdivision", "#b7daf8", "#2f74c0")),
        ("swatch", ("West Subdivision Jurisdiction (37 – 39)", "#c8efbf", "#3e9a45") if kind == "traffic" else ("West Subdivision", "#c8efbf", "#3e9a45")),
        ("red", "Traffic West Division Boundary" if kind == "traffic" else "West Division Boundary"),
        ("yellow", "Major Road / National Highway"),
        ("gray", "Other Road"),
    ]
    y = 0.262
    for kind_item, payload in items:
        if kind_item == "pin":
            ax.add_patch(Circle((0.652, y), 0.008, transform=ax.transAxes, fc="#d61c24", ec="white", lw=0.5, zorder=9))
            ax.text(0.675, y, payload, transform=ax.transAxes, ha="left", va="center", fontsize=5.7, zorder=9)
        elif kind_item == "swatch":
            label, fill, edge = payload
            ax.add_patch(Rectangle((0.640, y - 0.008), 0.026, 0.016, transform=ax.transAxes, fc=fill, ec=edge, lw=0.6, zorder=9))
            ax.text(0.675, y, label, transform=ax.transAxes, ha="left", va="center", fontsize=5.7, zorder=9)
        elif kind_item == "red":
            ax.plot([0.640, 0.668], [y, y], transform=ax.transAxes, color="#e10600", lw=2.2, zorder=9, solid_capstyle="round")
            ax.text(0.675, y, payload, transform=ax.transAxes, ha="left", va="center", fontsize=5.7, zorder=9)
        elif kind_item == "yellow":
            ax.plot([0.640, 0.668], [y, y], transform=ax.transAxes, color=ROAD_YELLOW, lw=2.4, zorder=9, solid_capstyle="round")
            ax.text(0.675, y, payload, transform=ax.transAxes, ha="left", va="center", fontsize=5.7, zorder=9)
        else:
            ax.plot([0.640, 0.668], [y, y], transform=ax.transAxes, color="#b9bdc6", lw=1.6, zorder=9)
            ax.text(0.675, y, payload, transform=ax.transAxes, ha="left", va="center", fontsize=5.7, zorder=9)
        y -= 0.032


def place_name_labels(fig, ax, rows: list[dict], kind: str, obstacles: list[tuple[float, float, float, float]] | None = None) -> None:
    """Put each name in the nearest free slot around its pin."""
    located = [row for row in rows if row["latitude"] is not None]
    pin_xy = [np.array(ax.transData.transform((row["longitude"], row["latitude"]))) for row in located]
    radii = (24, 36, 50) if kind == "traffic" else (18, 28, 40, 54)
    fontsize = 7.2 if kind == "traffic" else 5.6
    scale = fig.dpi / 72
    taken: list[tuple[float, float, float, float]] = list(obstacles or [])

    def box_for(origin, text, dx, dy):
        lines = text.split("\n")
        width = max(len(line) for line in lines) * fontsize * 0.62 * scale
        height = (len(lines) * fontsize * 1.35 + 6) * scale
        cx = origin[0] + dx * scale
        cy = origin[1] + dy * scale
        left = cx if dx >= 0 else cx - width
        bottom = cy - height / 2
        return (left, bottom, left + width, bottom + height)

    def overlaps(box, other) -> bool:
        return box[0] < other[2] and box[2] > other[0] and box[1] < other[3] and box[3] > other[1]

    order = sorted(
        range(len(located)),
        key=lambda index: min((np.linalg.norm(pin_xy[index] - other) for j, other in enumerate(pin_xy) if j != index), default=999),
    )
    chosen = {}
    for index in order:
        best = None
        best_score = None
        for radius in radii:
            for angle in range(0, 360, 20):
                dx = math.cos(math.radians(angle)) * radius
                dy = math.sin(math.radians(angle)) * radius
                box = box_for(pin_xy[index], located[index]["map_name"], dx, dy)
                center = np.array([(box[0] + box[2]) / 2, (box[1] + box[3]) / 2])
                hits_pin = any(np.linalg.norm(center - pin) < 34 or (box[0] - 4 < pin[0] < box[2] + 4 and box[1] - 4 < pin[1] < box[3] + 4) for pin in pin_xy)
                hits_label = any(overlaps(box, other) for other in taken)
                outside = box[0] < 0 or box[1] < 0
                nearest = min((other for j, other in enumerate(pin_xy) if j != index), key=lambda pin: np.linalg.norm(pin - pin_xy[index]), default=pin_xy[index])
                away = math.degrees(math.atan2(pin_xy[index][1] - nearest[1], pin_xy[index][0] - nearest[0]))
                delta = abs((angle - away + 180) % 360 - 180)
                score = hits_label * 10 + hits_pin * 8 + outside * 6 + delta / 90 + radius / 40
                if best_score is None or score < best_score:
                    best = (dx, dy, box)
                    best_score = score
                if score == 0:
                    break
            if best_score == 0:
                break
        chosen[index] = best
        taken.append(best[2])
    for index, (dx, dy, _box) in chosen.items():
        row = located[index]
        ax.annotate(
            row["map_name"],
            xy=(row["longitude"], row["latitude"]),
            xytext=(dx, dy),
            textcoords="offset points",
            fontsize=fontsize,
            fontweight="bold",
            color="#1a1a1a",
            ha="left" if dx >= 0 else "right",
            va="center",
            linespacing=0.9,
            path_effects=halo(2.6),
            zorder=9,
        )


def draw_map(fig, kind: str, rows: list[dict], roads: list[dict], field) -> None:
    image, (west_b, east_b, south_b, north_b) = fetch_basemap()
    ax = fig.add_axes([0.242, 0.012, 0.748, 0.838])
    ax.imshow(np.asarray(image), extent=(west_b, east_b, south_b, north_b), origin="upper", zorder=0, interpolation="bilinear")
    ax.set_xlim(WEST, EAST)
    ax.set_ylim(SOUTH, NORTH)
    ax.set_axis_off()
    lon_grid, lat_grid, colours, smooth = field
    ax.contourf(lon_grid, lat_grid, colours, levels=[-0.5, 0.5, 1.5, 2.5], colors=[group["fill"] for group in GROUPS], alpha=0.78, antialiased=True, zorder=2)
    ax.contour(lon_grid, lat_grid, smooth, levels=[0.42], colors=["#e10600"], linewidths=2.4, zorder=6)
    draw_roads(ax, roads)
    pins = {row["number"]: pin_image(row["number"], kind) for row in rows if row["latitude"] is not None}
    located = [row for row in rows if row["latitude"] is not None]
    for row in located:
        image_box = OffsetImage(pins[row["number"]], zoom=0.17 if kind == "traffic" else 0.135)
        ax.add_artist(AnnotationBbox(image_box, (row["longitude"], row["latitude"]), frameon=False, box_alignment=(0.5, 0.08), pad=0, zorder=8))
    badges = {
        0: (77.472, 12.972, "29 – 32"),
        1: (77.498, 13.078, "33 – 36"),
        2: (77.498, 12.898, "37 – 39"),
    }
    obstacles = []
    for x0, y0, x1, y1 in ((0.615, 0.012, 0.995, 0.335), (0.90, 0.78, 0.99, 0.93)):
        left, bottom = ax.transAxes.transform((x0, y0))
        right, top = ax.transAxes.transform((x1, y1))
        obstacles.append((min(left, right), min(bottom, top), max(left, right), max(bottom, top)))
    for lon, lat, _count in badges.values():
        px, py = ax.transData.transform((lon, lat))
        obstacles.append((px - 78, py - 16, px + 78, py + 16))
    place_name_labels(fig, ax, located, kind, obstacles)
    for group_index, group in enumerate(GROUPS):
        members = [row for row in located if row["acp"] == group["acp"]]
        lon, lat, traffic_count = badges[group_index]
        count = traffic_count if kind == "traffic" else f"{len(members)} stations"
        ax.text(
            lon,
            lat,
            f"ACP Traffic {group['name']} Subdivision\n({count})",
            ha="center",
            va="center",
            color="white",
            fontsize=6.3,
            fontweight="bold",
            zorder=7,
            bbox={"boxstyle": "round,pad=0.32", "fc": group["header"], "ec": "none"},
        )
    draw_compass(fig)
    draw_legend(ax, kind)
    ax.text(0.012, 0.012, "© OpenStreetMap  ·  © CARTO", transform=ax.transAxes, fontsize=5, color="#667085", zorder=9)


def page_rows(kind: str) -> list[dict]:
    numbers = TRAFFIC_NUMBERS if kind == "traffic" else LAW_NUMBERS
    rows = []
    for station in STATIONS:
        if station["id"] not in numbers:
            continue
        if (kind == "traffic" and station["type"] != "traffic") or (kind == "law" and station["type"] != "law_and_order"):
            continue
        row = dict(station)
        row["number"] = numbers[station["id"]]
        short = station["short_name"].replace(" Traffic", "")
        if kind == "traffic":
            row["list_name"] = f"{short} Traffic PS"
        else:
            row["list_name"] = f"{short} PS"
        row["map_name"] = short
        rows.append(row)
    return sorted(rows, key=lambda row: row["number"])


def render(pdf, kind: str, roads: list[dict], field) -> None:
    rows = page_rows(kind)
    fig = plt.figure(figsize=(16.54, 11.0), dpi=150)
    fig.patch.set_facecolor("white")
    if kind == "traffic":
        draw_header(fig, "TRAFFIC WEST DIVISION", "Traffic Police Stations – Jurisdiction Map (11 Stations)")
    else:
        draw_header(fig, "WEST DIVISION", "Law & Order Police Stations – Map (28 Stations)")
    draw_sidebar(fig, kind, rows)
    draw_map(fig, kind, rows, roads, field)
    fig.savefig(ROOT / "output" / f"poster_{kind}.png", dpi=130)
    pdf.savefig(fig)
    plt.close(fig)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    roads = fetch_roads()
    field = region_field()
    with PdfPages(OUT) as pdf:
        render(pdf, "traffic", roads, field)
        render(pdf, "law", roads, field)
    print(OUT)


if __name__ == "__main__":
    main()
