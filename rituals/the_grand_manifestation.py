#!/usr/bin/env python3
"""The Grand Manifestation (TUI-Safe Edition)."""
import sys, os, uuid, time, json, httpx, concurrent.futures, threading
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.live import Live
from rich.table import Table

sys.path.insert(0, os.path.abspath("."))

from engine.db.session import SessionLocal, init_db
from engine.db.models import Faction, ObserverNode
from engine.schemas.spectral import SpectralResonanceIngest, SpectralConstant
from engine.core.services import SpectralIntegrationService

console = Console()
stop_stream = threading.Event()

def strike_paradox(observer_id: uuid.UUID):
    db = SessionLocal()
    try:
        payload = SpectralResonanceIngest(
            observer_id=observer_id, primary_constant=SpectralConstant.GOLD_JOY,
            secondary_constant=SpectralConstant.BLUE_SORROW, magnitude=9.5, harmonic_phase=3.14159
        )
        SpectralIntegrationService.integrate_event(payload, db)
    finally:
        db.close()

def run_crucible(observer_id: uuid.UUID):
    time.sleep(2)
    console.print("[bold red][CRUCIBLE] Unleashing 50 threads of pure contradiction...[/bold red]")
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        for _ in range(50): executor.submit(strike_paradox, observer_id)
            
    time.sleep(5)
    console.print("[bold green][RECONCILIATION] The storm passes. Annealing the glass...[/bold green]")
    db = SessionLocal()
    from engine.schemas.reconciliation import ReconciliationEventPayload
    from engine.core.services import ReconciliationService
    ReconciliationService.anneal_observer(ReconciliationEventPayload(
        observer_id=observer_id, work_magnitude=0.8, scars_to_neutralize=5, justification="The storm passes."
    ), db)
    db.close()
    time.sleep(3)
    stop_stream.set()

def generate_layout(state_data):
    layout = Layout()
    layout.split_column(Layout(name="header", size=3), Layout(name="body"))
    layout["body"].split_row(Layout(name="left", ratio=1), Layout(name="right", ratio=1))

    layout["header"].update(Panel("[bold cyan]THE GLASS CATHEDRAL: LIVE SHADER UNIFORMS[/bold cyan]", style="bold white on black"))

    integrity = state_data.get("somatic_integrity", 1.0)
    thermal = min(state_data.get("thermal_load", 0.0), 50.0) / 50.0
    velocity = state_data.get("dialetheic_velocity", 0.0)
    scars = state_data.get("active_harmonic_scars", 0)

    metrics = Table.grid(padding=1)
    metrics.add_column(style="cyan", justify="right")
    metrics.add_column(style="magenta")
    metrics.add_row("u_somatic_integrity", f"{integrity:.3f}")
    metrics.add_row("u_thermal_load (Norm)", f"{thermal:.2f}")
    metrics.add_row("u_dialetheic_velocity", f"{velocity:.2f}")
    metrics.add_row("u_active_harmonic_scars", str(scars))
    layout["left"].update(Panel(metrics, title="[bold]Structural Telemetry[/bold]", border_style="green"))

    progress = Progress(
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(bar_width=None, complete_style="red", finished_style="green"),
        TextColumn("[bold yellow]{task.percentage:>3.0f}%"), expand=True
    )
    progress.add_task("Luminosity (Alpha)", total=100, completed=integrity * 100)
    progress.add_task("Heat Distortion (IOR)", total=100, completed=thermal * 100)
    progress.add_task("Chromatic Aberration", total=100, completed=velocity * 100)
    progress.add_task("Voronoi Fracture Density", total=100, completed=min(scars * 10, 100))
    layout["right"].update(Panel(progress, title="[bold]GLSL Uniform Simulation[/bold]", border_style="magenta"))

    return layout

def main():
    init_db()
    db = SessionLocal()
    obs = db.query(ObserverNode).filter(ObserverNode.designation == "Chaos-Subject").first()
    if not obs:
        fac = db.query(Faction).first()
        if not fac:
            fac = Faction(designation="Chaos-Faction")
            db.add(fac); db.commit(); db.refresh(fac)
        obs = ObserverNode(designation="Chaos-Subject", faction_id=fac.id)
        db.add(obs); db.commit(); db.refresh(obs)
    
    observer_id, faction_id = obs.observer_id, obs.faction_id
    db.close()

    console.print("\n[bold red]=== THE GRAND MANIFESTATION ===[/bold red]")
    console.print("[cyan]Connecting to SSE stream...[/cyan]\n")

    crucible_thread = threading.Thread(target=run_crucible, args=(observer_id,))
    crucible_thread.start()

    url = f"http://localhost:8000/api/v1/cathedral/stream/{faction_id}"
    
    try:
        # Removed screen=True to prevent terminal emulator freezing
        with httpx.stream("GET", url, timeout=None) as response:
            with Live(generate_layout({"somatic_integrity": 1.0}), console=console, refresh_per_second=4) as live:
                buffer = ""
                for chunk in response.iter_text():
                    if stop_stream.is_set(): break
                    buffer += chunk
                    while "\n\n" in buffer:
                        message, buffer = buffer.split("\n\n", 1)
                        if message.startswith("data: "):
                            payload_data = json.loads(message[6:])
                            observers = payload_data.get("observers", [])
                            if observers:
                                state = observers[0]
                                state["sequence_id"] = payload_data.get("sequence_id")
                                live.update(generate_layout(state))
    except KeyboardInterrupt:
        pass
    except Exception as e:
        console.print(f"[bold red]Stream Error: {e}[/bold red]")
    finally:
        stop_stream.set()
        crucible_thread.join()

    console.print("\n[bold green]The storm has passed. The glass holds.[/bold green]\n")

if __name__ == "__main__":
    main()
