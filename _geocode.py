"""Query Nominatim for each West Division station. Saves raw hits. Rate-limited."""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path(r"C:\Projects\TrafficWest\_nominatim_raw.json")
UA = "TrafficWestDivisionMap/1.0 (academic GIS research; Bengaluru police station coordinates)"

STATIONS = [
    "Magadi Road Traffic Police Station Bengaluru",
    "Vijayanagara Traffic Police Station Bengaluru",
    "Vijayanagar Traffic Police Station Bengaluru",
    "Kamakshipalya Traffic Police Station Bengaluru",
    "Kamakshi Palya Traffic Police Station Bengaluru",
    "Jnanabharathi Traffic Police Station Bengaluru",
    "Jnana Bharathi Traffic Police Station Bengaluru",
    "Magadi Road Police Station Bengaluru",
    "K.P. Agrahara Police Station Bengaluru",
    "KP Agrahara Police Station Bengaluru",
    "Vijayanagara Police Station Bengaluru",
    "Vijayanagar Police Station Bengaluru",
    "Govindarajanagar Police Station Bengaluru",
    "Govindaraj Nagar Police Station Bengaluru",
    "Basaveshwaranagar Police Station Bengaluru",
    "Basaveshwara Nagar Police Station Bengaluru",
    "Kamakshipalya Police Station Bengaluru",
    "Byadarahalli Police Station Bengaluru",
    "A.P. Nagar Police Station Bengaluru",
    "Annapurneshwari Nagar Police Station Bengaluru",
    "Jnanabharathi Police Station Bengaluru",
    "Malleshwaram Traffic Police Station Bengaluru",
    "Rajajinagar Traffic Police Station Bengaluru",
    "Rajajinagara Traffic Police Station Bengaluru",
    "Peenya Traffic Police Station Bengaluru",
    "Sadashivanagar Traffic Police Station Bengaluru",
    "Sadashivanagara Traffic Police Station Bengaluru",
    "Malleshwaram Police Station Bengaluru",
    "Subramanyanagar Police Station Bengaluru",
    "Subramanya Nagar Police Station Bengaluru",
    "Srirampura Police Station Bengaluru",
    "Rajajinagar Police Station Bengaluru",
    "Mahalakshmi Layout Police Station Bengaluru",
    "Nandini Layout Police Station Bengaluru",
    "Rajagopalanagar Police Station Bengaluru",
    "Rajagopala Nagar Police Station Bengaluru",
    "Peenya Police Station Bengaluru",
    "Madanayakanahalli Police Station Bengaluru",
    "Sadashivanagar Police Station Bengaluru",
    "Byatarayanapura Traffic Police Station Bengaluru",
    "Kengeri Traffic Police Station Bengaluru",
    "Girinagar Traffic Police Station Bengaluru",
    "Girinagara Traffic Police Station Bengaluru",
    "Byatarayanapura Police Station Bengaluru",
    "Chandra Layout Police Station Bengaluru",
    "Girinagar Police Station Bengaluru",
    "Hanumanthanagar Police Station Bengaluru",
    "Hanumantha Nagar Police Station Bengaluru",
    "C.K. Achukattu Police Station Bengaluru",
    "CK Achukattu Police Station Bengaluru",
    "K.G. Nagar Police Station Bengaluru",
    "KG Nagara Police Station Bengaluru",
    "Kengeri Police Station Bengaluru",
    "Rajarajeshwarinagar Police Station Bengaluru",
    "Rajarajeshwari Nagara Police Station Bengaluru",
    "Kumbalagodu Police Station Bengaluru",
    "Kumblugodu Police Station Bengaluru",
]

def nominatim(q):
    params = urllib.parse.urlencode({
        "q": q,
        "format": "jsonv2",
        "addressdetails": 1,
        "limit": 5,
        "countrycodes": "in",
    })
    url = "https://nominatim.openstreetmap.org/search?" + params
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode())

results = {}
if OUT.exists():
    results = json.loads(OUT.read_text(encoding="utf-8"))

for q in STATIONS:
    if q in results:
        print("skip", q)
        continue
    try:
        hits = nominatim(q)
    except Exception as e:
        print("ERR", q, e)
        results[q] = {"error": str(e)}
        OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
        time.sleep(1.2)
        continue
    slim = []
    for h in hits:
        slim.append({
            "lat": h.get("lat"),
            "lon": h.get("lon"),
            "display_name": h.get("display_name"),
            "type": h.get("type"),
            "class": h.get("class"),
            "osm_type": h.get("osm_type"),
            "osm_id": h.get("osm_id"),
            "importance": h.get("importance"),
        })
    results[q] = slim
    print(f"\n=== {q} ({len(slim)}) ===")
    for s in slim:
        print(f"  {s['lat']},{s['lon']} [{s['class']}/{s['type']}] {s['display_name'][:140]}")
    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    time.sleep(1.15)

print("\nDONE", len(results))
