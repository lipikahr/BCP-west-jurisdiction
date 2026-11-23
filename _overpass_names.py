import json
import urllib.request
from pathlib import Path

queries = {
    "west_police_name": """[out:json][timeout:90];
(
  nwr["name"~"Police",i](12.82,77.40,13.14,77.62);
);
out tags center;
""",
    "madanayakana": """[out:json][timeout:40];
(
  nwr["name"~"Madanayakana|Madanayakanahalli|Police",i](12.98,77.22,13.18,77.45);
);
out tags center;
""",
    "keywords": """[out:json][timeout:60];
(
  nwr["name"~"Kamakshi|Agrahara|Govindaraja|Annapurneshwari|Jnanabharathi|Jnana Bharathi|Hanumantha|Girinagar|Byatarayanapura|Byatarayana|Kengeri Traffic|Magadi Road Traffic|Peenya Traffic|Rajajinagar Traffic|Malleshwaram Traffic|Sadashiva|Mahalakshmi Layout|Rajagopala|K G Nagar|KG Nagar|Kempegowda Nagar",i](12.82,77.35,13.16,77.65);
);
out tags center;
""",
}

url = "https://overpass-api.de/api/interpreter"
all_out = {}
for key, q in queries.items():
    print("QUERY", key)
    req = urllib.request.Request(
        url,
        data=q.encode(),
        headers={"User-Agent": "TrafficWestDivisionMap/1.0 (academic GIS research)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.loads(r.read().decode())
    except Exception as e:
        print("FAIL", key, e)
        continue
    all_out[key] = data
    print(" elements", len(data.get("elements", [])))
    for e in data.get("elements", []):
        tags = e.get("tags") or {}
        lat = e.get("lat") or (e.get("center") or {}).get("lat")
        lon = e.get("lon") or (e.get("center") or {}).get("lon")
        name = tags.get("name", "")
        # keyword query is broad; print all. police-name query print all too but skip obvious highways if huge
        if key == "keywords" and "police" not in name.lower() and "traffic" not in name.lower():
            continue
        print(f"  {lat:.6f},{lon:.6f} | {name} | {tags.get('amenity','')} | {e.get('type')}/{e.get('id')}")

Path(r"c:\Projects\TrafficWest\_osm_names.json").write_text(
    json.dumps(all_out), encoding="utf-8"
)
print("WROTE")
