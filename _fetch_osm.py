import json
import time
import urllib.request
from pathlib import Path

ENDPOINTS = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]

# West and near-west Bengaluru tiles
BOXES = [
    (12.85, 77.40, 13.05, 77.52),
    (12.85, 77.52, 13.05, 77.62),
    (13.00, 77.45, 13.15, 77.62),
    (12.85, 77.40, 12.95, 77.55),
]

UA = "TrafficWestDivisionMap/1.0 (academic GIS research)"


def fetch(endpoint, query):
    req = urllib.request.Request(
        endpoint,
        data=query.encode(),
        headers={"User-Agent": UA, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=150) as r:
        return json.loads(r.read().decode())


all_elements = {}
for box in BOXES:
    s, w, n, e = box
    q = f"""[out:json][timeout:90];
(
  node["amenity"="police"]({s},{w},{n},{e});
  way["amenity"="police"]({s},{w},{n},{e});
  relation["amenity"="police"]({s},{w},{n},{e});
  node["name"~"[Pp]olice",i]({s},{w},{n},{e});
  way["name"~"[Pp]olice",i]({s},{w},{n},{e});
);
out center tags;
"""
    data = None
    for ep in ENDPOINTS:
        try:
            print("try", ep, box)
            data = fetch(ep, q)
            print("  ok", len(data.get("elements", [])))
            break
        except Exception as ex:
            print("  fail", type(ex).__name__, ex)
            time.sleep(2)
    if not data:
        continue
    for el in data.get("elements", []):
        key = f"{el.get('type')}/{el.get('id')}"
        all_elements[key] = el
    time.sleep(1.5)

out = Path(r"C:\Projects\TrafficWest\_osm_police.json")
payload = {"elements": list(all_elements.values())}
out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
print("UNIQUE", len(payload["elements"]))
for e in payload["elements"]:
    tags = e.get("tags") or {}
    lat = e.get("lat") or (e.get("center") or {}).get("lat")
    lon = e.get("lon") or (e.get("center") or {}).get("lon")
    name = tags.get("name", "")
    if not name:
        continue
    print(f"{lat:.5f},{lon:.5f} | {name} | amenity={tags.get('amenity','')} | {e.get('type')}/{e.get('id')}")
