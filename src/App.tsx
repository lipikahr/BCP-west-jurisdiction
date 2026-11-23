import { useMemo, useState } from "react";
import stationsJson from "./data/stations.json";
import type { Station } from "./types/station";
import { ACP_ORDER } from "./types/station";
import { plottedStations, validateStations } from "./utils/validation";
import { FilterPanel, type Filters } from "./components/FilterPanel";
import { Header, type MapModule } from "./components/Header";
import { Legend } from "./components/Legend";
import { MapView } from "./components/MapView";
import { SearchBox } from "./components/SearchBox";
import { SummaryPanel } from "./components/SummaryPanel";
import { AcpJurisdictionView, LawOrderDivisionView, TrafficDivisionView } from "./components/TrafficDivisionView";

const stations = stationsJson as Station[];

function allFilters(): Filters {
  return { acps: new Set(ACP_ORDER), traffic: true, law: true, labels: true };
}

export default function App() {
  const issues = useMemo(() => validateStations(stations), []);
  const errors = issues.filter((issue) => issue.level === "error");
  const warnings = issues.filter((issue) => issue.level === "warning");
  const [filters, setFilters] = useState<Filters>(allFilters);
  const [fitToken, setFitToken] = useState(0);
  const [focusId, setFocusId] = useState<string | null>(null);
  const [notice, setNotice] = useState("");
  const [module, setModule] = useState<MapModule>("stations");

  const visible = useMemo(
    () =>
      plottedStations(stations).filter((station) => {
        if (!filters.acps.has(station.acp)) return false;
        if (station.type === "traffic" && !filters.traffic) return false;
        if (station.type === "law_and_order" && !filters.law) return false;
        return true;
      }),
    [filters],
  );

  function selectStation(station: Station) {
    if (!station.coordinate_verified || station.latitude == null || station.longitude == null) {
      setNotice(`${station.name} has no verified coordinate, so it is not on the map.`);
      setFocusId(null);
      return;
    }
    setFilters({
      acps: new Set(filters.acps).add(station.acp),
      traffic: station.type === "traffic" ? true : filters.traffic,
      law: station.type === "law_and_order" ? true : filters.law,
      labels: filters.labels,
    });
    setNotice("");
    setFocusId(station.id);
  }

  if (errors.length > 0) {
    return (
      <main className="fatal">
        <h1>Station data failed validation</h1>
        <ul>
          {errors.map((issue) => (
            <li key={issue.message}>{issue.message}</li>
          ))}
        </ul>
      </main>
    );
  }

  return (
    <div className="app">
      <Header module={module} onModule={setModule} />
      {module === "traffic" ? (
        <TrafficDivisionView stations={stations} />
      ) : module === "law" ? (
        <LawOrderDivisionView stations={stations} />
      ) : module === "vijayanagara" ? (
        <AcpJurisdictionView stations={stations} acp="ACP Traffic – Vijayanagara" />
      ) : module === "peenya" ? (
        <AcpJurisdictionView stations={stations} acp="ACP Traffic – Peenya" />
      ) : module === "west" ? (
        <AcpJurisdictionView stations={stations} acp="ACP Traffic – West" />
      ) : (
        <>
      <aside>
        <SummaryPanel stations={stations} />
        <SearchBox stations={stations} onSelect={selectStation} />
        <FilterPanel
          filters={filters}
          onChange={setFilters}
          onShowAll={() => {
            setFilters(allFilters());
            setFitToken((n) => n + 1);
          }}
          onHideAll={() => setFilters({ acps: new Set(), traffic: false, law: false, labels: filters.labels })}
          onReset={() => {
            setFilters(allFilters());
            setFocusId(null);
            setNotice("");
            setFitToken((n) => n + 1);
          }}
        />
        <Legend />
        {warnings.length > 0 && (
          <section className="warning">
            <h2>Coordinate check</h2>
            {warnings.map((issue) => (
              <p key={issue.message}>{issue.message}</p>
            ))}
          </section>
        )}
        {notice && <p className="notice">{notice}</p>}
      </aside>
      <MapView stations={visible} fitToken={fitToken} focusId={focusId} showLabels={filters.labels} />
        </>
      )}
    </div>
  );
}
