/**
 * Coordinates are collected before the app runs.
 * The map does not geocode station names at runtime and does not estimate locations.
 * Each plotted station uses the latitude and longitude read from its Google Maps place pin.
 */
export const COORDINATE_SOURCE = "Google Maps";

export function formatCoordinate(value: number | null): string {
  if (value == null || Number.isNaN(value)) return "Not verified";
  return value.toFixed(6);
}
