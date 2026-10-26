"use client";

import { useEffect, useState } from "react";

type Asset = { id: number; hostname: string; display_name: string; authorized: boolean };
const API = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export default function Home() {
  const [health, setHealth] = useState("Checking");
  const [assets, setAssets] = useState<Asset[]>([]);
  const [error, setError] = useState("");

  async function refresh() {
    try {
      const h = await fetch(`${API}/health`, { cache: "no-store" });
      if (!h.ok) throw new Error("API health request failed");
      setHealth((await h.json()).status);
      const a = await fetch(`${API}/api/assets`, { cache: "no-store" });
      if (!a.ok) throw new Error("Asset request failed");
      setAssets(await a.json());
      setError("");
    } catch {
      setHealth("Unavailable");
      setError(`Cannot reach API at ${API}. Start the FastAPI backend and refresh.`);
    }
  }

  useEffect(() => { void refresh(); const id = setInterval(() => void refresh(), 10000); return () => clearInterval(id); }, []);

  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">S</span><div><strong>SHADOWBYTE</strong><small>CYBER OPERATIONS</small></div></div>
        <nav><a className="active">Overview</a><a>Assets</a><a>Assessments</a><a>Threat map</a><a>Reports</a><a>Settings</a></nav>
        <div className="sidebar-foot"><span className="dot" /> Local development environment</div>
      </aside>
      <section className="main">
        <header><div><p className="eyebrow">OPERATIONS CENTER / OVERVIEW</p><h1>Security overview</h1><p className="muted">Live data from your local ShadowByte API.</p></div><button onClick={() => void refresh()}>Refresh data ↻</button></header>
        {error && <div className="warning">{error}</div>}
        <div className="grid">
          <article className="metric"><span>API STATUS</span><strong className={health === "ok" ? "green" : ""}>{health}</strong><small>Polled every 10 seconds</small></article>
          <article className="metric"><span>REGISTERED ASSETS</span><strong>{assets.length}</strong><small>Persisted API records</small></article>
          <article className="metric"><span>AUTHORIZED ASSETS</span><strong>{assets.filter(a => a.authorized).length}</strong><small>Authorization metadata recorded</small></article>
        </div>
        <div className="section-head"><div><h2>Asset inventory</h2><p className="muted">No sample assets are inserted automatically.</p></div><span className="pill">REAL API DATA</span></div>
        <div className="table-wrap"><table><thead><tr><th>ASSET</th><th>HOSTNAME</th><th>AUTHORIZATION</th><th>RECORD ID</th></tr></thead><tbody>
          {assets.map(a => <tr key={a.id}><td>{a.display_name || "Unnamed asset"}</td><td className="mono">{a.hostname}</td><td><span className={`status ${a.authorized ? "good" : "pending"}`}>{a.authorized ? "Recorded" : "Not recorded"}</span></td><td>AS-{String(a.id).padStart(4, "0")}</td></tr>)}
          {assets.length === 0 && <tr><td colSpan={4} className="empty">No assets registered. Add an asset through the documented API.</td></tr>}
        </tbody></table></div>
        <div className="notice"><strong>Assessment safety</strong><p>Only run assessments on assets for which you have permission. The current starter profile performs DNS and TLS checks on a registered hostname; unrestricted scanning and remote shell access are not enabled.</p></div>
        <footer>SHADOWBYTE · DEFEND. MONITOR. ANALYZE. <span>Development build · 0.1.0</span></footer>
      </section>
    </main>
  );
}
