import { useEffect, useRef, type MutableRefObject } from "react";
import { MapContainer, TileLayer, useMap } from "react-leaflet";
import L from "leaflet";
import type { Station } from "../types/station";
import { JurisdictionPolygons } from "./JurisdictionPolygons";
import { StationMarker } from "./StationMarker";

function FitBounds({ stations, token }: { stations: Station[]; token: number }) {
  const map = useMap();
  const fitted = useRef<number | null>(null);
  useEffect(() => {
    if (fitted.current === token) return;
    fitted.current = token;
    const points = stations
      .filter((s) => s.latitude != null && s.longitude != null)
      .map((s) => [s.latitude as number, s.longitude as number] as [number, number]);
    if (points.length === 0) return;
    map.fitBounds(points, { padding: [36, 36], maxZoom: 14 });
  }, [map, stations, token]);
  return null;
}

function FocusStation({
  stations,
  focusId,
  markers,
}: {
  stations: Array<Station & { latitude: number; longitude: number }>;
  focusId: string | null;
  markers: MutableRefObject<Record<string, L.Marker | null>>;
}) {
  const map = useMap();
  useEffect(() => {
    if (!focusId) return;
    const station = stations.find((item) => item.id === focusId);
    if (!station) return;
    map.flyTo([station.latitude, station.longitude], 17, { duration: 0.6 });
    const timer = window.setTimeout(() => markers.current[station.id]?.openPopup(), 700);
    return () => window.clearTimeout(timer);
  }, [focusId, map, markers, stations]);
  return null;
}

export function MapView({
  stations,
  fitToken,
  focusId,
  showLabels,
}: {
  stations: Array<Station & { latitude: number; longitude: number }>;
  fitToken: number;
  focusId: string | null;
  showLabels: boolean;
}) {
  const mapRef = useRef<L.Map | null>(null);
  const markers = useRef<Record<string, L.Marker | null>>({});

  function fullscreen() {
    const node = document.querySelector(".map-shell");
    if (!node) return;
    if (document.fullscreenElement) void document.exitFullscreen();
    else void node.requestFullscreen();
  }

  return (
    <div className="map-shell">
      <MapContainer
        center={[12.97, 77.53]}
        zoom={12}
        ref={mapRef}
        zoomControl
        scrollWheelZoom
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <FitBounds stations={stations} token={fitToken} />
        <FocusStation stations={stations} focusId={focusId} markers={markers} />
        <JurisdictionPolygons stations={stations} />
        {stations.map((station) => (
          <StationMarker
            key={station.id}
            station={station}
            showLabel={showLabels}
            onBind={(id, marker) => {
              markers.current[id] = marker;
            }}
          />
        ))}
      </MapContainer>
      <div className="map-tools">
        <button type="button" onClick={() => mapRef.current?.setView([12.97, 77.53], 12)}>
          West overview
        </button>
        <button
          type="button"
          onClick={() => {
            const points = stations.map((s) => [s.latitude, s.longitude] as [number, number]);
            if (points.length) mapRef.current?.fitBounds(points, { padding: [36, 36], maxZoom: 14 });
          }}
        >
          View all stations
        </button>
        <button type="button" onClick={fullscreen}>Full screen</button>
      </div>
    </div>
  );
}
