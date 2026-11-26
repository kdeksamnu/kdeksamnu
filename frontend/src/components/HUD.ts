export class HUD {
  private el: HTMLElement;

  constructor(containerId: string) {
    this.el = document.getElementById(containerId) || document.body;
    this.init();
    this.poll();
    setInterval(() => this.poll(), 3000);
  }

  private init() {
    this.el.innerHTML = `
      <div style="background: rgba(15,15,21,0.85); border: 1px solid #242436; padding: 10px 14px; border-radius: 6px; color: #f3f4f6; font-size: 12px; line-height: 1.6;">
        <div style="color: #00e5ff; font-weight: bold; letter-spacing: 0.05em;">CATHEDRAL // RUNTIME</div>
        <div>SUBSTRATE: <span id="telemetry-status" style="color: #10b981;">CONNECTING...</span></div>
        <div>LATTICE: <span style="color: #a855f7;">FOUR {T, F, B, N}</span></div>
        <div>LATENCY: <span id="telemetry-latency">-- ms</span></div>
      </div>
    `;
  }

  private async poll() {
    const t0 = performance.now();
    try {
      const res = await fetch('/health');
      const data = await res.json();
      const dt = Math.round(performance.now() - t0);
      const statusEl = document.getElementById('telemetry-status');
      const latEl = document.getElementById('telemetry-latency');
      if (statusEl) statusEl.innerText = (data.status || 'ONLINE').toUpperCase();
      if (latEl) latEl.innerText = `${dt} ms`;
    } catch {
      const statusEl = document.getElementById('telemetry-status');
      if (statusEl) {
        statusEl.innerText = 'OFFLINE';
        statusEl.style.color = '#ef4444';
      }
    }
  }
}
