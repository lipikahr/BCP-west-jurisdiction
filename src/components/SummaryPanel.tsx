import type { Station } from "../types/station";
import { ACP_ORDER } from "../types/station";

export function SummaryPanel({ stations }: { stations: Station[] }) {
  const traffic = stations.filter((s) => s.type === "traffic").length;
  const law = stations.filter((s) => s.type === "law_and_order").length;
  const acps = new Set(stations.map((s) => s.acp)).size;
  const plotted = stations.filter((s) => s.coordinate_verified).length;

  return (
    <section className="summary">
      <p className="kicker">Bengaluru Traffic West Division</p>
      <div className="stats">
        <div><strong>{stations.length}</strong><span>Total stations</span></div>
        <div><strong>{law}</strong><span>Law &amp; Order</span></div>
        <div><strong>{traffic}</strong><span>Traffic</span></div>
        <div><strong>{acps}</strong><span>ACP sub-divisions</span></div>
      </div>
      <ul className="acp-counts">
        {ACP_ORDER.map((acp) => (
          <li key={acp}>
            <span>{acp.replace("ACP Traffic – ", "")}</span>
            <strong>{stations.filter((s) => s.acp === acp).length}</strong>
          </li>
        ))}
      </ul>
      <p className="plotted">{plotted} plotted from verified Google Maps pins</p>
    </section>
  );
}
