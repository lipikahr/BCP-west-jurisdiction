import { Polygon, Tooltip } from "react-leaflet";
import type { Station } from "../types/station";
import { jurisdictionAreas } from "../data/jurisdictions";

export function JurisdictionPolygons({ stations }: { stations: Station[] }) {
  const visible = new Set(stations.map((station) => station.id));
  const areas = jurisdictionAreas.filter((area) => area.stationIds.some((id) => visible.has(id)));
  return (
    <>
      {areas.flatMap((area) =>
        area.rings.map((ring, index) => (
          <Polygon
            key={`${area.name}-${index}`}
            positions={ring}
            pathOptions={{ color: area.colour, weight: 2, fillColor: area.colour, fillOpacity: 0.2 }}
          >
            <Tooltip sticky>{area.name}</Tooltip>
          </Polygon>
        )),
      )}
    </>
  );
}
