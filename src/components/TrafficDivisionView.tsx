import { useEffect, useMemo, useRef, useState } from "react";
import { MapContainer, TileLayer, useMap } from "react-leaflet";
import L from "leaflet";
import type { Station, StationType } from "../types/station";
import { ACP_ORDER, typeLabel } from "../types/station";
import { TRAFFIC_STATION_NUMBERS } from "../data/trafficNumbers";
import { LAW_ORDER_STATION_NUMBERS } from "../data/lawOrderNumbers";
import { JurisdictionPolygons } from "./JurisdictionPolygons";
import { StationMarker } from "./StationMarker";
import { plottedStations } from "../utils/validation";

function FitOnce({ points }: { points: Array<[number, number]> }) {
  const map = useMap();
  const done = useRef(false);
  useEffect(() => {
    if (done.current || points.length === 0) return;
    done.current = true;
    map.fitBounds(points, { padding: [48, 48], maxZoom: 13 });
  }, [map, points]);
  return null;
}

function GroupedStationView({
  stations,
  type,
  numbers,
  kicker,
  title,
  note,
  markerLabel,
  sampleBadge,
}: {
  stations: Station[];
  type: StationType;
  numbers: Record<string, number>;
  kicker: string;
  title: string;
  note: string;
  markerLabel: string;
  sampleBadge: string;
}) {
  const [focusId, setFocusId] = useState<string | null>(null);
  const markers = useRef<Record<string, L.Marker | null>>({});
  const mapRef = useRef<L.Map | null>(null);

  const listed = useMemo(
    () =>
      stations
        .filter((station) => station.type === type)
        .sort((a, b) => a.short_name.localeCompare(b.short_name, "en", { sensitivity: "base" })),
    [stations, type],
  );
  const plotted = plottedStations(listed);

  return (
    <>
      <aside>
        <section className="summary traffic-intro">
          <p className="kicker">{kicker}</p>
          <h2>{title}</h2>
          <p className="legend-note">{note}</p>
        </section>
        <ol className="traffic-list">
          {listed.map((station) => {
            const number = numbers[station.id];
            return (
              <li key={station.id}>
                <button
                  type="button"
                  onClick={() => {
                    if (!station.coordinate_verified) return;
                    setFocusId(station.id);
                    if (station.latitude != null && station.longitude != null) {
                      mapRef.current?.flyTo([station.latitude, station.longitude], 15, { duration: 0.5 });
                      window.setTimeout(() => markers.current[station.id]?.openPopup(), 600);
                    }
                  }}
                >
                  <span className="num" style={{ background: station.acp_colour }}>{number}</span>
                  <span>
                    <strong>{station.short_name}</strong>
                    <em>{station.coordinate_verified ? station.acp.replace("ACP Traffic – ", "") : "Coordinate not verified"}</em>
                  </span>
                </button>
              </li>
            );
          })}
        </ol>
        <section className="legend">
          <h2>Legend</h2>
          <ul>
            {ACP_ORDER.map((acp) => {
              const colour = stations.find((station) => station.acp === acp)?.acp_colour ?? "#64748b";
              return (
                <li key={acp}>
                  <span className="swatch" style={{ background: colour }} />
                  {acp.replace("ACP Traffic – ", "")} jurisdiction
                </li>
              );
            })}
            <li>
              <span className={`pin badge sample ${type}`}>{sampleBadge}</span>
              {markerLabel}
            </li>
          </ul>
        </section>
      </aside>
      <div className="map-shell">
        <MapContainer center={[12.97, 77.53]} zoom={12} ref={mapRef} zoomControl scrollWheelZoom>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <FitOnce points={plotted.map((station) => [station.latitude, station.longitude])} />
          <JurisdictionPolygons stations={plotted} />
          {plotted.map((station) => (
            <StationMarker
              key={`${station.id}-${focusId === station.id ? "on" : "off"}`}
              station={station}
              showLabel
              badge={String(numbers[station.id] ?? "")}
              onBind={(id, marker) => {
                markers.current[id] = marker;
              }}
            />
          ))}
        </MapContainer>
        <p className="map-caption">
          Shaded areas are pre-2022 Bengaluru Traffic Police jurisdictions from OpenCity. Stations that are not in that map have no boundary.
        </p>
      </div>
    </>
  );
}

export function TrafficDivisionView({ stations }: { stations: Station[] }) {
  return (
    <GroupedStationView
      stations={stations}
      type="traffic"
      numbers={TRAFFIC_STATION_NUMBERS}
      kicker="Traffic West Division"
      title="11 traffic police stations"
      note="Numbers 29–39 follow the 18 November 2026 gazette schedule. Shaded areas are the pre-2022 OpenCity traffic jurisdictions that contain these stations."
      markerLabel="Traffic police station"
      sampleBadge="29"
    />
  );
}

const STATION_NUMBERS = { ...LAW_ORDER_STATION_NUMBERS, ...TRAFFIC_STATION_NUMBERS };

export function AcpJurisdictionView({
  stations,
  acp,
}: {
  stations: Station[];
  acp: (typeof ACP_ORDER)[number];
}) {
  const [focusId, setFocusId] = useState<string | null>(null);
  const markers = useRef<Record<string, L.Marker | null>>({});
  const mapRef = useRef<L.Map | null>(null);
  const label = acp.replace("ACP Traffic – ", "");

  const listed = useMemo(
    () =>
      stations
        .filter((station) => station.acp === acp)
        .sort((a, b) => a.short_name.localeCompare(b.short_name, "en", { sensitivity: "base" })),
    [acp, stations],
  );
  const plotted = plottedStations(listed);
  const colour = listed.find((station) => station.acp_colour)?.acp_colour ?? "#64748b";
  const trafficCount = listed.filter((station) => station.type === "traffic").length;
  const lawCount = listed.length - trafficCount;

  return (
    <>
      <aside>
        <section className="summary traffic-intro">
          <p className="kicker">ACP jurisdiction</p>
          <h2>{label}</h2>
          <p className="legend-note">
            {listed.length} police stations: {trafficCount} traffic and {lawCount} law and order. Shaded areas are the pre-2022 OpenCity boundaries that match stations in this ACP. Stations missing from that map have no boundary.
          </p>
        </section>
        <ol className="traffic-list">
          {listed.map((station) => {
            const number = STATION_NUMBERS[station.id];
            return (
              <li key={station.id}>
                <button
                  type="button"
                  onClick={() => {
                    if (!station.coordinate_verified) return;
                    setFocusId(station.id);
                    if (station.latitude != null && station.longitude != null) {
                      mapRef.current?.flyTo([station.latitude, station.longitude], 15, { duration: 0.5 });
                      window.setTimeout(() => markers.current[station.id]?.openPopup(), 600);
                    }
                  }}
                >
                  <span className="num" style={{ background: station.acp_colour }}>{number}</span>
                  <span>
                    <strong>{station.short_name}</strong>
                    <em>{station.coordinate_verified ? typeLabel(station.type) : "Coordinate not verified"}</em>
                  </span>
                </button>
              </li>
            );
          })}
        </ol>
        <section className="legend">
          <h2>Legend</h2>
          <ul>
            <li>
              <span className="swatch" style={{ background: colour }} />
              {label} jurisdiction
            </li>
            <li>
              <span className="pin badge sample traffic">29</span>
              Traffic police station
            </li>
            <li>
              <span className="pin badge sample law_and_order">1</span>
              Law and order police station
            </li>
          </ul>
        </section>
      </aside>
      <div className="map-shell">
        <MapContainer center={[12.97, 77.53]} zoom={12} ref={mapRef} zoomControl scrollWheelZoom>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <FitOnce points={plotted.map((station) => [station.latitude, station.longitude])} />
          <JurisdictionPolygons stations={plotted} />
          {plotted.map((station) => (
            <StationMarker
              key={`${station.id}-${focusId === station.id ? "on" : "off"}`}
              station={station}
              showLabel
              badge={String(STATION_NUMBERS[station.id] ?? "")}
              onBind={(id, marker) => {
                markers.current[id] = marker;
              }}
            />
          ))}
        </MapContainer>
        <p className="map-caption">
          Shaded areas are pre-2022 Bengaluru Traffic Police jurisdictions from OpenCity for stations in {label}.
        </p>
      </div>
    </>
  );
}

export function LawOrderDivisionView({ stations }: { stations: Station[] }) {
  return (
    <GroupedStationView
      stations={stations}
      type="law_and_order"
      numbers={LAW_ORDER_STATION_NUMBERS}
      kicker="Traffic West Division"
      title="28 law and order police stations"
      note="Numbers 1–28 follow the 18 November 2026 gazette schedule. Shaded areas are the matching pre-2022 station boundaries from the OpenCity traffic jurisdiction map. Newer stations are not in that map."
      markerLabel="Law and order police station"
      sampleBadge="1"
    />
  );
}
