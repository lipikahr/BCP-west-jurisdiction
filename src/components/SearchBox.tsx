import { useMemo, useState } from "react";
import type { Station } from "../types/station";
import { typeLabel } from "../types/station";

export function SearchBox({
  stations,
  onSelect,
}: {
  stations: Station[];
  onSelect: (station: Station) => void;
}) {
  const [query, setQuery] = useState("");
  const results = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return [];
    return stations
      .filter((s) => `${s.name} ${s.short_name} ${s.google_place_name}`.toLowerCase().includes(q))
      .slice(0, 8);
  }, [query, stations]);

  return (
    <section className="search">
      <label htmlFor="station-search">Search stations</label>
      <input
        id="station-search"
        value={query}
        placeholder="Magadi"
        onChange={(event) => setQuery(event.target.value)}
      />
      {results.length > 0 && (
        <ul>
          {results.map((station) => (
            <li key={station.id}>
              <button
                type="button"
                onClick={() => {
                  onSelect(station);
                  setQuery("");
                }}
              >
                <strong>{station.name}</strong>
                <span>
                  {typeLabel(station.type)}
                  {station.coordinate_verified ? "" : " · not plotted"}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
