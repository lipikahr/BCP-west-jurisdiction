const GROUPS = [
  { name: "ACP Traffic – Vijayanagara", colour: "#1d4ed8" },
  { name: "ACP Traffic – Peenya", colour: "#15803d" },
  { name: "ACP Traffic – West", colour: "#dc2626" },
];

export function Legend() {
  return (
    <section className="legend">
      <h2>West Division</h2>
      <p className="legend-key">Colour is the ACP. Shape is the station type.</p>
      <ul>
        {GROUPS.map((group) => (
          <li key={group.name}>
            <span className="swatch" style={{ background: group.colour }} />
            {group.name}
          </li>
        ))}
        <li>
          <span className="pin traffic sample" style={{ background: "#334155" }} />
          Traffic Police Station
        </li>
        <li>
          <span className="pin law_and_order sample" style={{ background: "#334155" }} />
          Law &amp; Order Police Station
        </li>
      </ul>
      <p className="legend-note">
        Shaded areas are the pre-2022 OpenCity traffic jurisdictions that contain the plotted stations. Kumbalagodu and the Kengeri traffic pin are outside every boundary in that map.
      </p>
    </section>
  );
}
