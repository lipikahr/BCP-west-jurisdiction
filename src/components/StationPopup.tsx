import type { MouseEvent } from "react";
import type { Station } from "../types/station";
import { typeLabel } from "../types/station";
import { formatCoordinate } from "../utils/geocoding";

function mapsUrl(station: Station): string {
  if (station.google_maps_url.includes("!1s")) return station.google_maps_url;
  const place = station.google_place_name.trim() || `${station.name} Bengaluru`;
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(place)}`;
}

function openMaps(event: MouseEvent<HTMLAnchorElement>, url: string) {
  event.preventDefault();
  event.stopPropagation();
  const opened = window.open(url, "_blank", "noopener,noreferrer");
  if (!opened) window.location.assign(url);
}

export function StationPopup({ station }: { station: Station }) {
  const locationUrl = mapsUrl(station);
  return (
    <div className="popup">
      <h2>{station.name}</h2>
      {station.google_place_name && station.google_place_name !== station.name && (
        <p className="popup-place">Google Maps place: {station.google_place_name}</p>
      )}
      <dl>
        <dt>Type</dt>
        <dd>{typeLabel(station.type)}</dd>
        <dt>ACP</dt>
        <dd>{station.acp}</dd>
        <dt>Coordinates</dt>
        <dd>
          {formatCoordinate(station.latitude)}, {formatCoordinate(station.longitude)}
        </dd>
        <dt>Address</dt>
        <dd>{station.address || "Not listed"}</dd>
        {station.phone && (
          <>
            <dt>Phone</dt>
            <dd>{station.phone}</dd>
          </>
        )}
        <dt>Source</dt>
        <dd>{station.source}</dd>
        <dt>Location</dt>
        <dd>
          <a
            className="popup-link"
            href={locationUrl}
            target="_blank"
            rel="noopener noreferrer"
            onMouseDown={(event) => event.stopPropagation()}
            onClick={(event) => openMaps(event, locationUrl)}
          >
            Open in Google Maps
          </a>
        </dd>
      </dl>
      {station.notes && <p className="popup-note">{station.notes}</p>}
    </div>
  );
}
