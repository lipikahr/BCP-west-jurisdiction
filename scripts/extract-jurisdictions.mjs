// Builds src/data/jurisdictions.json from the OpenCity pre-2022 KML
// https://data.opencity.in/dataset/bengaluru-traffic-police-jurisdictions/resource/65302179-fb7f-46f4-8dbf-d9600a83e1ca
import fs from "fs";
import stations from "../src/data/stations.json" with { type: "json" };

const text = fs.readFileSync(process.argv[2], "utf8");
const lines = text.split(/\r?\n/);

function simplify(points, tol) {
  if (points.length <= 3) return points;
  const dist = (p, a, b) => {
    const dx = b[0] - a[0];
    const dy = b[1] - a[1];
    const len = dx * dx + dy * dy;
    if (len === 0) return Math.hypot(p[0] - a[0], p[1] - a[1]);
    let t = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / len;
    t = Math.max(0, Math.min(1, t));
    return Math.hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dy));
  };
  function dp(start, end, keep) {
    let max = 0;
    let idx = -1;
    for (let i = start + 1; i < end; i += 1) {
      const d = dist(points[i], points[start], points[end]);
      if (d > max) {
        max = d;
        idx = i;
      }
    }
    if (max > tol && idx !== -1) {
      dp(start, idx, keep);
      dp(idx, end, keep);
    } else keep.push(end);
  }
  const keep = [0];
  dp(0, points.length - 1, keep);
  keep.sort((a, b) => a - b);
  return keep.map((i) => points[i]);
}

function inside(lat, lng, ring) {
  let c = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [yi, xi] = ring[i];
    const [yj, xj] = ring[j];
    if (yi > lat !== yj > lat && lng < ((xj - xi) * (lat - yi)) / (yj - yi) + xi) c = !c;
  }
  return c;
}

let ps = null;
let tr = null;
let rings = [];
const features = [];

function flush() {
  if (tr && rings.length > 0) features.push({ ps, tr, rings });
  ps = null;
  tr = null;
  rings = [];
}

for (const raw of lines) {
  const t = raw.trim().replace(/\s+/g, " ");
  if (!t || t.includes("$")) continue;
  if (/traffic ps/i.test(t) && t.length < 80) {
    tr = t;
    continue;
  }
  if (/\bps$/i.test(t) && t.length < 80 && !/traffic/i.test(t)) {
    if (rings.length) flush();
    ps = t;
    continue;
  }
  if (/^\d{2}\.\d+,\d{1,2}\.\d+/.test(t)) {
    const pts = t
      .split(/\s+/)
      .map((pair) => {
        const [lng, lat] = pair.split(",").map(Number);
        return [lat, lng];
      })
      .filter((p) => Number.isFinite(p[0]) && Number.isFinite(p[1]));
    if (pts.length >= 4) rings.push(pts);
  }
}
if (rings.length) flush();

const plotted = stations.filter((station) => station.latitude != null && station.longitude != null);
const areas = [];

for (const feature of features) {
  const insideStations = plotted.filter((station) =>
    feature.rings.some((ring) => inside(station.latitude, station.longitude, ring)),
  );
  if (insideStations.length === 0) continue;
  const colour = insideStations[0].acp_colour;
  const simplified = feature.rings.map((ring) => {
    const closed =
      ring[0][0] === ring[ring.length - 1][0] && ring[0][1] === ring[ring.length - 1][1]
        ? ring
        : [...ring, ring[0]];
    let next = simplify(closed, 0.00008);
    if (next[0][0] !== next[next.length - 1][0] || next[0][1] !== next[next.length - 1][1]) {
      next = [...next, next[0]];
    }
    return next.map(([lat, lng]) => [Number(lat.toFixed(5)), Number(lng.toFixed(5))]);
  });
  areas.push({
    name: feature.tr,
    colour,
    stationIds: insideStations.map((station) => station.id),
    rings: simplified,
  });
  console.log(feature.tr, insideStations.map((station) => station.short_name).join(", "));
}

const target = new URL("../src/data/jurisdictions.json", import.meta.url);
fs.writeFileSync(target, JSON.stringify(areas));
console.log("areas", areas.length, "bytes", fs.statSync(target).size);
