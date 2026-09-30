import sys
import os
#!/usr/bin/env python3
"""CLI utility for direct terminal-based spectral event transduction."""
import uuid
import typer
from rich.console import Console
from rich.table import Table

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine.db.session import SessionLocal, init_db
from engine.db.models import ObserverNode, SpectralEvent, Faction
from engine.schemas.spectral import SpectralResonanceIngest, SpectralConstant
from engine.core.services import SpectralIntegrationService
from sqlalchemy import desc

app = typer.Typer(help="MLAOS-PRIME Rituals: Terminal Transduction Engine")
console = Console()

@app.command()
def init():
    init_db()
    console.print("[bold green]Ash Archive schema initialized successfully.[/bold green]")

@app.command()
def provision_observer(
    designation: str = typer.Argument(..., help="Unique moniker for the Warm Axis agent"),
    faction: str = typer.Option("unaligned", "--faction", "-f", help="Faction allegiance"),
):
    db = SessionLocal()
    try:
        observer = ObserverNode(designation=designation, faction=faction)
        db.add(observer)
        db.commit()
        db.refresh(observer)
        console.print(f"[bold green]Observer Provisioned:[/bold green] {observer.designation} (ID: {observer.observer_id})")
    except Exception as e:
        db.rollback()
        if "UNIQUE constraint failed" in str(e) or "unique constraint" in str(e).lower():
            console.print(f"[bold yellow]Observer '{designation}' already exists in the Ash Registry.[/bold yellow]")
        else:
            console.print(f"[bold red]Error:[/bold red] {e}")
    finally:
        db.close()

@app.command()
def list_observers():
    db = SessionLocal()
    try:
        observers = db.query(ObserverNode).all()
        if not observers:
            console.print("[yellow]No observers found in the Ash Archive.[/yellow]")
            return
        
        table = Table(title="Somatic Observer Registry")
        table.add_column("Designation", style="cyan")
        table.add_column("ID", style="magenta")
        table.add_column("Faction", style="green")
        table.add_column("Integrity", style="yellow")
        table.add_column("Scars", style="red")
        
        for obs in observers:
            table.add_row(
                obs.designation,
                str(obs.observer_id),
                obs.faction,
                f"{obs.somatic_integrity:.3f}",
                str(obs.harmonic_scars_total)
            )
        console.print(table)
    finally:
        db.close()

@app.command()
def bind_observer(
    observer: uuid.UUID = typer.Option(..., "--observer", "-o", help="UUID of the Somatic Observer"),
    faction: uuid.UUID = typer.Option(..., "--faction", "-f", help="UUID of the Ideological Collective"),
    proof_hash: str = typer.Option(..., "--proof-hash", "-p", help="SHA-256 state_hash of the observer's latest event")
):
    """Binds an observer to a faction, requiring cryptographic proof of their current state."""
    db = SessionLocal()
    try:
        # 1. Verify Observer
        obs = db.query(ObserverNode).filter(ObserverNode.observer_id == observer).first()
        if not obs:
            console.print("[bold red]Friction:[/bold red] Observer not found in the registry.")
            raise typer.Exit(code=1)
            
        # 2. Verify Faction
        fac = db.query(Faction).filter(Faction.id == faction).first()
        if not fac:
            console.print("[bold red]Friction:[/bold red] Faction not found in the registry.")
            raise typer.Exit(code=1)

        # 3. The Artificial Friction: Cryptographic Consent
        latest_event = db.query(SpectralEvent).filter(
            SpectralEvent.observer_id == observer
        ).order_by(desc(SpectralEvent.timestamp)).first()

        if not latest_event:
            console.print("[bold red]Friction:[/bold red] Observer has no event history. Cannot verify state.")
            raise typer.Exit(code=1)

        if latest_event.state_hash != proof_hash:
            console.print(f"[bold red]Friction:[/bold red] Cryptographic proof failed.")
            console.print(f"Expected: {latest_event.state_hash}")
            console.print(f"Provided: {proof_hash}")
            console.print("[italic]The observer's current state of decay does not match your claim. Binding denied.[/italic]")
            raise typer.Exit(code=1)

        # 4. Success: Apply the link
        obs.faction_id = faction
        db.commit()
        console.print(f"[bold green]Binding Successful:[/bold green] {obs.designation} has been anchored to {fac.designation}.")
        console.print(f"[dim]State verified at hash: {proof_hash[:16]}...[/dim]")
    finally:
        db.close()

@app.command()
def inject(
    observer: uuid.UUID = typer.Option(..., "--observer", "-o", help="UUID of the Somatic Observer"),
    primary: SpectralConstant = typer.Argument(..., help="Primary spectral constant"),
    secondary: SpectralConstant = typer.Option(None, "--secondary", "-s", help="Optional secondary constant"),
    magnitude: float = typer.Option(5.0, "--magnitude", "-m", min=0.0, max=10.0, help="Intensity [0-10]"),
    fracture: bool = typer.Option(False, "--fracture", "-f", help="Flag micro-fracture"),
    phase: float = typer.Option(0.0, "--phase", "-p", help="Harmonic phase in radians (topologically normalized to S^1)"),
):
    payload = SpectralResonanceIngest(
        observer_id=observer, primary_constant=primary, secondary_constant=secondary,
        magnitude=magnitude, micro_fracture_detected=fracture,
        harmonic_phase=phase,
    )
    db = SessionLocal()
    try:
        result = SpectralIntegrationService.integrate_event(payload, db)
        table = Table(title="Spectral Event Inscription Result")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="magenta")
        for k, v in result.items():
            table.add_row(k, str(v))
        console.print(table)
    finally:
        db.close()

@app.command()
def verify(event_id: uuid.UUID = typer.Argument(..., help="UUID of the event to audit")):
    db = SessionLocal()
    try:
        res = SpectralIntegrationService.verify_event_integrity(event_id, db)
        status_color = "green" if res["valid"] else "red"
        console.print(f"[{status_color}]Verification: {'VALID' if res['valid'] else 'COMPROMISED'}[/{status_color}]")
        table = Table(title=f"Merkle Audit for {event_id}")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="magenta")
        for k, v in res.items():
            table.add_row(k, str(v))
        console.print(table)
    finally:
        db.close()

if __name__ == "__main__":
    app()


@app.command()
def anneal(
    observer: uuid.UUID = typer.Option(..., "--observer", "-o", help="UUID of the Somatic Observer to anneal"),
    work: float = typer.Option(0.2, "--work", "-w", ge=0.01, le=1.0, help="Expenditure W_rec logged on-chain"),
    scars: int = typer.Option(1, "--scars", "-s", ge=0, help="Discrete units of active tension resolved")
):
    """M_5: Appends a Reconciliation Event to anneal active harmonic scars."""
    from engine.db.models import ObserverNode, SpectralEvent, SpectralConstantEnum, LogicStateEnum
    from sqlalchemy import desc
    import hashlib
    
    db = SessionLocal()
    try:
        obs = db.query(ObserverNode).filter(ObserverNode.observer_id == observer).first()
        if not obs:
            console.print("[bold red]Observer not found in the Somatic Registry.[/bold red]")
            raise typer.Exit(1)
            
        # 1. Fetch the parent hash from the terminal leaf
        last_event = db.query(SpectralEvent).filter(SpectralEvent.observer_id == observer).order_by(desc(SpectralEvent.timestamp)).first()
        parent_hash = last_event.state_hash if last_event else "0" * 64
        
        # 2. Compute the new state hash (Lex I compliance)
        event_uuid = uuid.uuid4()
        raw = f"{parent_hash}:{event_uuid}:{observer}:RECONCILIATION:{work}:{scars}"
        state_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        
        # 3. Append the Reconciliation Event to the Merkle DAG
        event = SpectralEvent(
            event_id=event_uuid,
            observer_id=observer,
            primary_constant=SpectralConstantEnum.BRONZE_OBSIDIAN_NULL,
            logic_state=LogicStateEnum.TRUE,
            magnitude=work,
            harmonic_phase=0.0,
            parent_hash=parent_hash,
            state_hash=state_hash,
            is_reconciliation=True,
            reconciliation_magnitude=work,
            scars_to_neutralize=scars
        )
        db.add(event)
        
        # 4. Fold the state (The Conservation Law)
        # Active scars decrement. Lifetime scars remain untouched.
        obs.active_harmonic_scars = max(0, obs.active_harmonic_scars - scars)
        
        # Hysteresis Impedance: Healing is harder the more scarred you are.
        lambda_imp = 0.25
        delta_integrity = 0.85 * (work / (1.0 + lambda_imp * obs.active_harmonic_scars))
        obs.somatic_integrity = min(1.0, obs.somatic_integrity + delta_integrity)
        
        db.commit()
        db.refresh(obs)
        
        console.print(f"[bold green]Annealing Complete.[/bold green]")
        console.print(f"  Somatic Integrity: [cyan]{obs.somatic_integrity:.4f}[/cyan]")
        console.print(f"  Active Scars:      [magenta]{obs.active_harmonic_scars}[/magenta]")
        console.print(f"  Lifetime Scars:    [yellow]{obs.lifetime_harmonic_scars}[/yellow] (Immutable)")
    finally:
        db.close()


@app.command()
def reconcile(
    observer: uuid.UUID = typer.Option(..., "--observer", "-o", help="UUID of the Somatic Observer"),
    work: float = typer.Option(0.2, "--work", "-w", ge=0.01, le=1.0, help="Verified work expenditure (W_rec)"),
    neutralize: int = typer.Option(1, "--neutralize", "-n", ge=0, help="Active scars to neutralize"),
    justification: str = typer.Option(..., "--justification", "-j", help="Reason for annealing")
):
    """Executes the Work-Coupled Annealing Protocol. Heals the glass without erasing the scars."""
    from engine.schemas.reconciliation import ReconciliationEventPayload
    from engine.core.services import ReconciliationService
    
    payload = ReconciliationEventPayload(
        observer_id=observer,
        work_magnitude=work,
        scars_to_neutralize=neutralize,
        justification=justification
    )
    
    db = SessionLocal()
    try:
        result = ReconciliationService.anneal_observer(payload, db)
        
        table = Table(title="Reconciliation Annealing Result", border_style="green")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        for k, v in result.items():
            table.add_row(k, str(v))
        console.print(table)
    finally:
        db.close()
