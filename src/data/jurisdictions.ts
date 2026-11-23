import raw from "./jurisdictions.json";

/** Pre-2022 Bengaluru Traffic Police jurisdictions, OpenCity resource 65302179-fb7f-46f4-8dbf-d9600a83e1ca. */
export interface JurisdictionArea {
  name: string;
  colour: string;
  stationIds: string[];
  rings: Array<Array<[number, number]>>;
}

export const jurisdictionAreas = raw as unknown as JurisdictionArea[];
