# Bengaluru Traffic West Division

Interactive map of the police stations grouped under the three Traffic ACP sub-divisions of Bengaluru Traffic West.

Colour shows the ACP. Marker shape shows the station type: a circle is a traffic police station, and a square is a law-and-order police station.

The map shows station locations. It does not draw jurisdiction boundaries. Official boundary polygons were not available, and none were invented.

## Run

```bash
npm install
npm run dev
```

Open http://localhost:5173

Check the dataset:

```bash
npm run validate
```

Validation exits with an error while Girinagar Traffic Police Station has no verified coordinate. The map still opens and leaves that station unplotted.

## Coordinates

Every plotted pin is the Google Maps place coordinate for that station. Coordinates were read from the place URL (`!3d` latitude, `!4d` longitude) after searching the station name. They were not estimated from neighbourhood names.

Where an OpenStreetMap `amenity=police` object is the same building, that is noted in `coordinate_verification.md` and in the station record.

## Grouping

ACP membership follows the supplied Word document and the grouping in the project brief. The Karnataka gazette of 18 November 2026 organises law-and-order stations under different ACP offices. That difference is recorded in the verification report and was not used to move stations.
