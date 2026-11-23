import { ACP_ORDER } from "../types/station";

export interface Filters {
  acps: Set<string>;
  traffic: boolean;
  law: boolean;
  labels: boolean;
}

export function FilterPanel({
  filters,
  onChange,
  onShowAll,
  onHideAll,
  onReset,
}: {
  filters: Filters;
  onChange: (filters: Filters) => void;
  onShowAll: () => void;
  onHideAll: () => void;
  onReset: () => void;
}) {
  function toggleAcp(acp: string) {
    const acps = new Set(filters.acps);
    if (acps.has(acp)) acps.delete(acp);
    else acps.add(acp);
    onChange({ ...filters, acps });
  }

  return (
    <section className="filters">
      <h2>ACP</h2>
      {ACP_ORDER.map((acp) => (
        <label key={acp}>
          <input type="checkbox" checked={filters.acps.has(acp)} onChange={() => toggleAcp(acp)} />
          {acp.replace("ACP Traffic – ", "")}
        </label>
      ))}
      <h2>Station type</h2>
      <label>
        <input
          type="checkbox"
          checked={filters.traffic}
          onChange={() => onChange({ ...filters, traffic: !filters.traffic })}
        />
        Traffic
      </label>
      <label>
        <input
          type="checkbox"
          checked={filters.law}
          onChange={() => onChange({ ...filters, law: !filters.law })}
        />
        Law &amp; Order
      </label>
      <h2>Labels</h2>
      <label>
        <input
          type="checkbox"
          checked={filters.labels}
          onChange={() => onChange({ ...filters, labels: !filters.labels })}
        />
        Name tags
      </label>
      <div className="filter-actions">
        <button type="button" onClick={onShowAll}>Show all</button>
        <button type="button" onClick={onHideAll}>Hide all</button>
        <button type="button" onClick={onReset}>Reset filters</button>
      </div>
    </section>
  );
}
