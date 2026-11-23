import { readFileSync, writeFileSync } from "node:fs";

const stations = JSON.parse(readFileSync(new URL("../src/data/stations.json", import.meta.url), "utf8"));
const rows = stations
  .map((s) =>
    `| ${[
      s.name,
      s.type === "traffic" ? "Traffic" : "Law & Order",
      s.acp.replace("ACP Traffic – ", ""),
      s.latitude ?? "—",
      s.longitude ?? "—",
      s.source,
      s.coordinate_verified ? "Yes" : "No",
    ].join(" | ")} |`,
  )
  .join("\n");
const names = stations
  .map((s) => `| ${s.name} | ${s.google_place_name || "—"} |`)
  .join("\n");

const md = `# Coordinate verification

Coordinates were read from Google Maps place pins on 23 November 2026. The latitude and longitude are the \`!3d\` and \`!4d\` values in the place URL. Neighbourhood centroids were not used.

38 stations are plotted. Girinagar Traffic Police Station is listed and is not plotted.

| Station | Type | ACP | Latitude | Longitude | Source | Verified |
|---|---|---|---|---|---|---|
${rows}

## Name on the Google place

| Document name | Google Maps place |
|---|---|
${names}

## Not plotted

Girinagar Traffic Police Station. Google Maps returned Girinagara Police Station and a place titled Girinagar Traffic Zone (12.9401397, 77.5475449, Vivekananda Park Road, Girinagar, phone 080 2294 3108). The traffic-zone place was not used because its title is not the police station. The law-and-order station was not reused.

## Stations that share a premises

These are separate Google place pins, not copied coordinates.

- Peenya Traffic Police Station and Peenya Police Station are a few metres apart on the Peenya station premises.
- Kengeri Traffic Police Station is at Kumbalagodu, beside Kumbalagodu Police Station, opposite RR Engineering College. Kengeri Police Station remains in Kengeri Satellite Town.
- Magadi Road Traffic Police Station and Magadi Road Police Station are adjacent in the Police Quarters, Rajajinagar.
- Malleshwaram Traffic Police Station and Malleshwara Police Station are adjacent.
- Sadashivanagar Traffic Police Station and Sadashivanagara Police Station are about 30 metres apart on New BEL Road.

## Discrepancies

The Word document is the grouping used on this map. It was not edited to match the newer gazette.

1. Karnataka Gazette notification HD/144 (i) /POP/2026, dated 18 November 2026, is newer than the proposal in the Word document. It places the 11 traffic stations under the same three Traffic ACPs, including Girinagar TR PS. The Word table names only 10 traffic stations and leaves the third West row blank. Girinagar Traffic Police Station is included because the project brief and the gazette both list it.
2. The same gazette places law-and-order stations under law-and-order ACPs (Vijayanagara, Malleshwaram, Rajajinagara, Kengeri, Byatarayanapura, Girinagara and Peenya), not under the Traffic ACPs. This map keeps the Word document's traffic-jurisdiction grouping.
3. K.P. Agrahara is mapped to Kempapura Agrahara Police Station. The phone 080 2294 2518 matches the Karnataka Police west-division directory.
4. A.P. Nagar is Annapurneshwari Nagar Police Station. The gazette lists Annapurneshwari Nagara PS, and the phone 080 2348 2644 matches the older Karnataka Police directory.
5. C.K. Achukattu is Chennamanakere Achukattu Police Station.
6. K.G. Nagar is Kempegowda Nagar Police Station, 56 KG Nagar Main Road, Gavipuram Guttahalli. A Wilson Garden result titled Kg Nagar police station was rejected.
7. The Word document spells Kumbalagodu as Kumblugodu. The gazette and Google use Kumbalagodu / Kumbalagudu.
8. Byatarayanapura Traffic and Byatarayanapura Police Station are the Mysore Road stations in Banashankari, not the northern Byatarayanapura near Yelahanka.

## Sources

- Google Maps place pins, searched by station name
- Karnataka Gazette, 18 November 2026: https://egazette.servantsofknowledge.in/details/in.gazette.karnataka_eo.2026-11-18.12898/
- Bengaluru Traffic Police contact list: https://btp.gov.in/Contactus.aspx
- Karnataka Police west-division directory: https://ksp.karnataka.gov.in/storage/pdf-files/west.pdf
- OpenStreetMap amenity=police, used only as a cross-check where the same building is mapped
`;

writeFileSync(new URL("../coordinate_verification.md", import.meta.url), md);
console.log("wrote report", stations.length);
