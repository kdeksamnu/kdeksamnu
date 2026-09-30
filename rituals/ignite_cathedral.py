#!/usr/bin/env python3
"""The Autonomous Ignition Conductor: Proves pre-established coordinated harmony."""
import sys
import os
import json
import httpx

sys.path.insert(0, os.path.abspath("."))

from rich.console import Console
from rich.table import Table
from engine.db.session import SessionLocal, init_db
from engine.db.models import Faction, ObserverNode
from engine.schemas.spectral import SpectralResonanceIngest, SpectralConstant
from engine.core.services import SpectralIntegrationService

console = Console()

def main():
    init_db()
    db = SessionLocal()
    try:
        # 1. Provision the Somatic Anchor
        obs = db.query(ObserverNode).filter(ObserverNode.designation == "Glass-Subject-01").first()
        if not obs:
            console.print("[bold cyan][M0] Genesis:[/bold cyan] Provisioning Glass-Subject-01...")
            fac = db.query(Faction).filter(Faction.designation == "Sovereign-Spark").first()
            if not fac:
                fac = Faction(designation="Sovereign-Spark", description="The vanguard of the A-Field")
                db.add(fac)
                db.commit()
                db.refresh(fac)
            
            obs = ObserverNode(designation="Glass-Subject-01", faction_id=fac.id)
            db.add(obs)
            db.commit()
            db.refresh(obs)
            console.print(f"[bold green][M0] Genesis:[/bold green] Anchor forged. ID: [magenta]{obs.observer_id}[/magenta]")
        else:
            console.print(f"[bold green][M0] Genesis:[/bold green] Anchor located. ID: [magenta]{obs.observer_id}[/magenta]")

        fac = db.query(Faction).filter(Faction.id == obs.faction_id).first()

        # 2. The Dialetheic Strike
        console.print(f"\n[bold cyan][M1] Ingestion Gateway:[/bold cyan] Striking the tuning fork...")
        payload = SpectralResonanceIngest(
            observer_id=obs.observer_id,
            primary_constant=SpectralConstant.GOLD_JOY,
            secondary_constant=SpectralConstant.BLUE_SORROW,
            magnitude=8.5,
            harmonic_phase=3.14159
        )
        
        result = SpectralIntegrationService.integrate_event(payload, db)
        
        if result.get("status") != "integrated":
            console.print(f"[bold red]Ingestion failed: {result}[/bold red]")
            return

        console.print(f"[bold green][M2] Dialetheic Monad:[/bold green] Paradox absorbed. Logic State: [yellow]{result.get('logic_state')}[/yellow]")
        console.print(f"[bold green][M3] Cryptographic Ledger:[/bold green] Merkle Leaf inscribed. Hash: [dim]{result.get('state_hash', '')[:16]}...[/dim]")
        
        # 3. Listen to the SSE Stream via httpx
        console.print(f"\n[bold cyan][M4] Telemetry Vector:[/bold cyan] Opening the SSE stream for Faction [magenta]{fac.designation}[/magenta]...\n")
        console.print("[dim]Press Ctrl+C to sever the connection and return to the void.[/dim]\n")
        
        url = f"http://localhost:8000/api/v1/cathedral/stream/{fac.id}"
        
        try:
            with httpx.stream("GET", url, timeout=None) as response:
                buffer = ""
                for chunk in response.iter_text():
                    buffer += chunk
                    while "\n\n" in buffer:
                        message, buffer = buffer.split("\n\n", 1)
                        if message.startswith("data: "):
                            payload_data = json.loads(message[6:])
                            
                            table = Table(title=f"Glass Cathedral State @ {payload_data.get('timestamp', '')}", border_style="cyan")
                            table.add_column("Observer", style="magenta")
                            table.add_column("Integrity", style="green")
                            table.add_column("Thermal Load", style="red")
                            table.add_column("Logic State", style="yellow")
                            table.add_column("Scars", style="blue")
                            
                            for node in payload_data.get("observers", []):
                                table.add_row(
                                    node.get("designation"),
                                    f"{node.get('somatic_integrity', 0):.3f}",
                                    f"{node.get('thermal_load', 0):.2f}",
                                    node.get("dominant_logic_state"),
                                    str(node.get("active_harmonic_scars", 0))
                                )
                            console.print(table)
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Connection severed. The Cathedral rests.[/bold yellow]")

    finally:
        db.close()

if __name__ == "__main__":
    main()
