export type StationType = "traffic" | "law_and_order";

export interface Station {
  id: string;
  name: string;
  short_name: string;
  type: StationType;
  acp: string;
  acp_colour: string;
  latitude: number | null;
  longitude: number | null;
  address: string;
  source: string;
  coordinate_verified: boolean;
  google_place_name: string;
  google_maps_url: string;
  phone: string;
  notes: string;
}

export const ACP_ORDER = [
  "ACP Traffic – Vijayanagara",
  "ACP Traffic – Peenya",
  "ACP Traffic – West",
] as const;

export function typeLabel(type: StationType): string {
  return type === "traffic" ? "Traffic Police Station" : "Law & Order Police Station";
}
