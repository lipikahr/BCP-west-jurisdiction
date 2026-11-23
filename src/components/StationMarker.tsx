import { useMemo } from "react";
import { Marker, Popup } from "react-leaflet";
import L from "leaflet";
import type { Station } from "../types/station";
import { StationPopup } from "./StationPopup";

export function StationMarker({
  station,
  onBind,
  showLabel = true,
  badge,
}: {
  station: Station & { latitude: number; longitude: number };
  onBind: (id: string, marker: L.Marker | null) => void;
  showLabel?: boolean;
  badge?: string;
}) {
  const icon = useMemo(() => {
    const pin = badge
      ? `<span class="pin badge ${station.type}" style="background:${station.acp_colour}">${badge}</span>`
      : `<span class="pin ${station.type}" style="background:${station.acp_colour}"></span>`;
    const label = showLabel ? `<span class="pin-label">${station.short_name}</span>` : "";
    return L.divIcon({
      className: "station-marker",
      html: `<span class="pin-row">${pin}${label}</span>`,
      iconSize: [16, 16],
      iconAnchor: [8, 8],
      popupAnchor: [0, -12],
    });
  }, [badge, showLabel, station.acp_colour, station.short_name, station.type]);

  return (
    <Marker
      position={[station.latitude, station.longitude]}
      icon={icon}
      ref={(marker) => onBind(station.id, marker)}
      zIndexOffset={station.type === "traffic" ? 200 : 100}
    >
      <Popup>
        <StationPopup station={station} />
      </Popup>
    </Marker>
  );
}
