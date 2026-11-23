/** Convex hull of [latitude, longitude] points. Used only to group plotted stations. */
export function convexHull(points: Array<[number, number]>): Array<[number, number]> {
  const unique = new Map<string, [number, number]>();
  for (const point of points) unique.set(`${point[0].toFixed(6)},${point[1].toFixed(6)}`, point);
  const sorted = [...unique.values()].sort((a, b) => (a[1] === b[1] ? a[0] - b[0] : a[1] - b[1]));
  if (sorted.length <= 2) return sorted;

  const cross = (o: [number, number], a: [number, number], b: [number, number]) =>
    (a[1] - o[1]) * (b[0] - o[0]) - (a[0] - o[0]) * (b[1] - o[1]);

  const lower: Array<[number, number]> = [];
  for (const point of sorted) {
    while (lower.length >= 2 && cross(lower[lower.length - 2], lower[lower.length - 1], point) <= 0) {
      lower.pop();
    }
    lower.push(point);
  }
  const upper: Array<[number, number]> = [];
  for (let i = sorted.length - 1; i >= 0; i -= 1) {
    const point = sorted[i];
    while (upper.length >= 2 && cross(upper[upper.length - 2], upper[upper.length - 1], point) <= 0) {
      upper.pop();
    }
    upper.push(point);
  }
  upper.pop();
  lower.pop();
  return [...lower, ...upper];
}

export function expandFromCenter(ring: Array<[number, number]>, factor = 1.18): Array<[number, number]> {
  if (ring.length === 0) return ring;
  const lat = ring.reduce((sum, point) => sum + point[0], 0) / ring.length;
  const lng = ring.reduce((sum, point) => sum + point[1], 0) / ring.length;
  return ring.map(([y, x]) => [lat + (y - lat) * factor, lng + (x - lng) * factor]);
}
