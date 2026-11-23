import { readFileSync } from "node:fs";

const stations = JSON.parse(readFileSync(new URL("../src/data/stations.json", import.meta.url), "utf8"));
const errors = [];
const warnings = [];
const BENGALURU = { minLat: 12.7, maxLat: 13.2, minLon: 77.3, maxLon: 77.8 };
const ACP = [
  "ACP Traffic – Vijayanagara",
  "ACP Traffic – Peenya",
  "ACP Traffic – West",
];

if (stations.length !== 39) errors.push(`Expected 39 stations, found ${stations.length}.`);
const traffic = stations.filter((s) => s.type === "traffic");
const law = stations.filter((s) => s.type === "law_and_order");
if (traffic.length !== 11) errors.push(`Expected 11 traffic stations, found ${traffic.length}.`);
if (law.length !== 28) errors.push(`Expected 28 law-and-order stations, found ${law.length}.`);

const acps = new Set(stations.map((s) => s.acp));
if (acps.size !== 3) errors.push(`Expected 3 ACP groups, found ${acps.size}.`);
for (const acp of ACP) if (!acps.has(acp)) errors.push(`Missing ACP group ${acp}.`);

const ids = new Set();
const coords = new Map();
for (const station of stations) {
  if (ids.has(station.id)) errors.push(`Duplicate id ${station.id}.`);
  ids.add(station.id);
  if (station.type !== "traffic" && station.type !== "law_and_order") {
    errors.push(`${station.name} has an invalid type.`);
  }
  if (!ACP.includes(station.acp)) errors.push(`${station.name} is not in exactly one known ACP.`);
  if (!station.source) errors.push(`${station.name} has no coordinate source.`);

  const plotted = station.coordinate_verified === true && station.latitude != null && station.longitude != null;
  if (!plotted) {
    warnings.push(`${station.name} has no verified coordinate.`);
    if (station.coordinate_verified) errors.push(`${station.name} is marked verified without coordinates.`);
    continue;
  }
  if (
    station.latitude < BENGALURU.minLat || station.latitude > BENGALURU.maxLat ||
    station.longitude < BENGALURU.minLon || station.longitude > BENGALURU.maxLon
  ) {
    errors.push(`${station.name} is outside the Bengaluru window.`);
  }
  const key = `${station.latitude.toFixed(5)},${station.longitude.toFixed(5)}`;
  if (coords.has(key)) errors.push(`${station.name} shares coordinates with ${coords.get(key)}.`);
  coords.set(key, station.name);
}

const counts = Object.fromEntries(ACP.map((acp) => [acp, stations.filter((s) => s.acp === acp).length]));
console.log("Stations", stations.length);
console.log("Traffic", traffic.length, "Law & Order", law.length);
console.log("By ACP", counts);
console.log("Plotted", stations.filter((s) => s.coordinate_verified).length);

if (warnings.length) {
  console.log("\nNeeds manual verification:");
  for (const warning of warnings) console.log(" -", warning);
}
if (errors.length) {
  console.log("\nErrors:");
  for (const error of errors) console.log(" -", error);
  process.exit(1);
}
if (warnings.length) process.exit(1);
console.log("\nValidation passed.");
