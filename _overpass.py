import json
import urllib.request
from pathlib import Path

q = """[out:json][timeout:90];
(
  nwr["amenity"="police"](12.80,77.35,13.15,77.75);
);
out center tags;
"""
endpoints = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://overpass.openstreetmap.fr/api/interpreter",
]
last = None
for url in endpoints:
    try:
        req = urllib.request.Request(
            url,
            data=q.encode(),
            headers={"User-Agent": "TrafficWestDivisionMap/1.0 (academic GIS research)"},
        )
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.loads(r.read().decode())
        print("OK", url, "elements", len(data.get("elements", [])))
        Path(r"c:\Projects\TrafficWest\_osm_police.json").write_text(
            json.dumps(data, indent=2), encoding="utf-8"
        )
        for e in data.get("elements", []):
            tags = e.get("tags") or {}
            lat = e.get("lat") or (e.get("center") or {}).get("lat")
            lon = e.get("lon") or (e.get("center") or {}).get("lon")
            print(f"{lat:.6f},{lon:.6f} | {tags.get('name','')} | {e.get('type')}/{e.get('id')}")
        break
    except Exception as e:
        print("FAIL", url, type(e).__name__, e)
        last = e
else:
    raise SystemExit("all overpass failed")
