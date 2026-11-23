import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

QUERIES = [
    "Magadi Road Traffic Police Station",
    "Kamakshipalya Traffic Police Station",
    "Traffic Police Station Kamakshipalya",
    "Jnanabharathi Traffic Police Station",
    "Jnana Bharathi Police Station",
    "K.P. Agrahara Police Station",
    "KP Agrahara Police Station",
    "Govindarajanagar Police Station",
    "Govindaraj Nagar Police Station",
    "Kamakshipalya Police Station",
    "Annapurneshwari Nagar Police Station",
    "Malleshwaram Traffic Police Station",
    "Malleshwaram Police Station",
    "Rajajinagar Traffic Police Station",
    "Rajajinagar Police Station",
    "Peenya Traffic Police Station",
    "Sadashivanagar Traffic Police Station",
    "Sadashivanagar Police Station",
    "Mahalakshmi Layout Police Station",
    "Rajagopalanagar Police Station",
    "Madanayakanahalli Police Station",
    "Byatarayanapura Traffic Police Station",
    "Byatarayanapura Police Station",
    "Kengeri Traffic Police Station",
    "Girinagar Traffic Police Station",
    "Hanumanthanagar Police Station",
    "Hanumantha Nagar Police Station",
    "C K Achukattu Police Station",
    "K G Nagar Police Station",
    "Rajarajeshwari Nagar Police Station",
    "Jnanabharathi Police Station",
]

out = {}
path = Path(r"c:\Projects\TrafficWest\_photon_raw.json")
for q in QUERIES:
    params = urllib.parse.urlencode({
        "q": q + " Bengaluru",
        "lat": "12.98",
        "lon": "77.54",
        "limit": "6",
        "lang": "en",
    })
    url = "https://photon.komoot.io/api/?" + params
    req = urllib.request.Request(url, headers={"User-Agent": "TrafficWestDivisionMap/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
    except Exception as e:
        print("ERR", q, e)
        out[q] = {"error": str(e)}
        time.sleep(0.4)
        continue
    feats = []
    for f in data.get("features", []):
        props = f.get("properties") or {}
        coords = (f.get("geometry") or {}).get("coordinates") or [None, None]
        feats.append({
            "lon": coords[0],
            "lat": coords[1],
            "name": props.get("name"),
            "osm_key": props.get("osm_key"),
            "osm_value": props.get("osm_value"),
            "osm_id": props.get("osm_id"),
            "osm_type": props.get("osm_type"),
            "city": props.get("city") or props.get("county"),
            "street": props.get("street"),
            "postcode": props.get("postcode"),
        })
    out[q] = feats
    print(f"\n=== {q} ({len(feats)}) ===")
    for s in feats:
        print(f"  {s['lat']},{s['lon']} [{s['osm_key']}={s['osm_value']}] {s['name']} | {s['street']} | {s['city']}")
    time.sleep(0.35)

path.write_text(json.dumps(out, indent=2), encoding="utf-8")
print("DONE")
