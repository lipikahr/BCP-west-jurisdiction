import type { Station } from "../types/station";
import { ACP_ORDER } from "../types/station";

export interface ValidationIssue {
  level: "error" | "warning";
  message: string;
}

const BENGALURU = { minLat: 12.7, maxLat: 13.2, minLon: 77.3, maxLon: 77.8 };

export function validateStations(stations: Station[]): ValidationIssue[] {
  const issues: ValidationIssue[] = [];
  const ids = new Set<string>();
  const coords = new Map<string, string>();

  if (stations.length !== 39) {
    issues.push({ level: "error", message: `Expected 39 stations, found ${stations.length}.` });
  }

  const traffic = stations.filter((s) => s.type === "traffic").length;
  const law = stations.filter((s) => s.type === "law_and_order").length;
  if (traffic !== 11) issues.push({ level: "error", message: `Expected 11 traffic stations, found ${traffic}.` });
  if (law !== 28) issues.push({ level: "error", message: `Expected 28 law-and-order stations, found ${law}.` });

  const acps = new Set(stations.map((s) => s.acp));
  if (acps.size !== 3) issues.push({ level: "error", message: `Expected 3 ACP groups, found ${acps.size}.` });
  for (const acp of ACP_ORDER) {
    if (!acps.has(acp)) issues.push({ level: "error", message: `Missing ACP group ${acp}.` });
  }

  for (const station of stations) {
    if (ids.has(station.id)) issues.push({ level: "error", message: `Duplicate id ${station.id}.` });
    ids.add(station.id);

    if (station.type !== "traffic" && station.type !== "law_and_order") {
      issues.push({ level: "error", message: `${station.name} has an invalid station type.` });
    }
    if (!station.acp) issues.push({ level: "error", message: `${station.name} has no ACP.` });
    if (!station.source) issues.push({ level: "error", message: `${station.name} has no coordinate source.` });

    if (!station.coordinate_verified || station.latitude == null || station.longitude == null) {
      issues.push({
        level: "warning",
        message: `${station.name} has no verified coordinate and is not plotted.`,
      });
      continue;
    }

    const latitude = station.latitude;
    const longitude = station.longitude;
    if (
      latitude < BENGALURU.minLat ||
      latitude > BENGALURU.maxLat ||
      longitude < BENGALURU.minLon ||
      longitude > BENGALURU.maxLon
    ) {
      issues.push({
        level: "error",
        message: `${station.name} is outside the Bengaluru coordinate window (${latitude}, ${longitude}).`,
      });
    }

    const key = `${latitude.toFixed(5)},${longitude.toFixed(5)}`;
    const other = coords.get(key);
    if (other) {
      issues.push({
        level: "error",
        message: `${station.name} shares coordinates with ${other}.`,
      });
    }
    coords.set(key, station.name);
  }

  return issues;
}

export function plottedStations(
  stations: Station[],
): Array<Station & { latitude: number; longitude: number }> {
  return stations.filter(
    (s): s is Station & { latitude: number; longitude: number } =>
      s.coordinate_verified && s.latitude != null && s.longitude != null,
  );
}
