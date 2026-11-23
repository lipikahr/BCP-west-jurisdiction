export type MapModule = "stations" | "traffic" | "law" | "vijayanagara" | "peenya" | "west";

const MODULES: Array<{ id: MapModule; label: string }> = [
  { id: "stations", label: "All stations" },
  { id: "traffic", label: "Traffic division" },
  { id: "law", label: "Law & Order" },
  { id: "vijayanagara", label: "ACP Vijayanagara" },
  { id: "peenya", label: "ACP Peenya" },
  { id: "west", label: "ACP West" },
];

export function Header({ module, onModule }: { module: MapModule; onModule: (module: MapModule) => void }) {
  return (
    <header className="site-header">
      <div className="brand">
        <img src="/bcp-logo.png" alt="Bengaluru City Police" />
        <div className="brand-text">
          <p>West Commissionerate</p>
          <h1>Bangalore West Division Police Stations Jurisdiction Map</h1>
        </div>
      </div>
      <nav className="module-switch" aria-label="Map views">
        {MODULES.map((item) => (
          <button
            key={item.id}
            type="button"
            className={module === item.id ? "on" : ""}
            onClick={() => onModule(item.id)}
          >
            {item.label}
          </button>
        ))}
      </nav>
    </header>
  );
}
