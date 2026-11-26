export interface ConstraintNode {
  id: number;
  label: string;
  name: string;
  error: number; // r_i residual
  target: number;
  dialetheic: boolean;
}

export interface KineticPass {
  id: number;
  label: string;
  name: string;
  momentum: number; // p_j
}

export class SomaticSolver {
  public M: number[][] = []; // 12 x 11 coupling matrix (132 channels)
  public constraints: ConstraintNode[] = [];
  public passes: KineticPass[] = [];
  public K: number = 0.15; // Feedback gain
  public sparsity_p: number = 0.15;
  public importance_I: number = 1.2;
  public phaseRegime: 'Orthogonal' | 'ETF / Simplex' | 'Cross-Polytope (Antipodal)' = 'Orthogonal';

  // 4D Tesseract Vector Frame (16 Boolean Unit Vertices)
  public hypercubeVertices: number[][] = [];
  public selectedVector: number = 3;

  constructor() {
    this.initConstraints();
    this.initPasses();
    this.initMatrix();
    this.initHypercube();
  }

  private initConstraints() {
    const names = [
      'C1: Ground Reaction Conservation',
      'C2: Calcaneal Momentum Balance',
      'C3: Tibiofemoral Kinetic Vector',
      'C4: Dialetheic Tension Containment',
      'C5: Lex I Additive Scars',
      'C6: Thoracolumbar Shear Alignment',
      'C7: Scapular Glide Orthogonality',
      'C8: Glenohumeral Torque Equilibrium',
      'C9: Antebrachial Torsional Invariant',
      'C10: Carpal Phase Articulation',
      'C11: Manus Mudrā Trajectory Seal',
      'C12: Somatic Terminal Closure'
    ];
    this.constraints = names.map((name, i) => ({
      id: i,
      label: `C${i + 1}`,
      name,
      error: 0.0,
      target: 1.0,
      dialetheic: i === 3 // C4 is Dialetheic
    }));
  }

  private initPasses() {
    const names = [
      'P1: Floor Interface',
      'P2: Calcaneal Pivot',
      'P3: Tibial Fulcrum',
      'P4: Lumbar Spine Torsion',
      'P5: Thoracic Core Hub',
      'P6: Cervical Axis',
      'P7: Scapular Glide Plate',
      'P8: Brachial Lever',
      'P9: Antebrachial Twist',
      'P10: Carpal Articulation',
      'P11: Manus / Mudrā Claws'
    ];
    this.passes = names.map((name, i) => ({
      id: i,
      label: `P${i + 1}`,
      name,
      momentum: 0.5 + Math.sin(i) * 0.2
    }));
  }

  private initMatrix() {
    this.M = Array.from({ length: 12 }, (_, i) =>
      Array.from({ length: 11 }, (_, j) => {
        const val = 0.5 + 0.45 * Math.sin(i * 1.3 + j * 0.9);
        return parseFloat(val.toFixed(3));
      })
    );
  }

  private initHypercube() {
    this.hypercubeVertices = [];
    for (let i = 0; i < 16; i++) {
      this.hypercubeVertices.push([
        (i & 1) ? 1 : -1,
        (i & 2) ? 1 : -1,
        (i & 4) ? 1 : -1,
        (i & 8) ? 1 : -1
      ]);
    }
  }

  /// 60 FPS Closed-Loop Feedback Step: p_{n+1} = p_n + K * M^T * (c* - M * p_n)
  public step(time: number) {
    // 1. Compute M * p
    const Mp = new Array(12).fill(0);
    for (let i = 0; i < 12; i++) {
      for (let j = 0; j < 11; j++) {
        Mp[i] += this.M[i][j] * this.passes[j].momentum;
      }
    }

    // 2. Residual r = c* - M*p
    for (let i = 0; i < 12; i++) {
      const target = this.constraints[i].target + (this.constraints[i].dialetheic ? Math.sin(time * 3.0) * 0.6 : 0.0);
      this.constraints[i].error = parseFloat((target - Mp[i]).toFixed(3));
    }

    // 3. Update p_{n+1}
    for (let j = 0; j < 11; j++) {
      let grad = 0.0;
      for (let i = 0; i < 12; i++) {
        grad += this.M[i][j] * this.constraints[i].error;
      }
      this.passes[j].momentum = Math.max(0.05, Math.min(2.5, this.passes[j].momentum + this.K * grad * 0.1));
    }

    // 4. Update Superposition Phase Regime
    if (this.sparsity_p < 0.25) {
      this.phaseRegime = 'Orthogonal';
    } else if (this.sparsity_p <= 0.65) {
      this.phaseRegime = 'ETF / Simplex';
    } else {
      this.phaseRegime = 'Cross-Polytope (Antipodal)';
    }
  }

  public getAntipodalVector(k: number): number {
    return 15 - k;
  }
}
