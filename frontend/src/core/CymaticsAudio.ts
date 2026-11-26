export class CymaticsAudio {
  private ctx: AudioContext | null = null;
  private osc1: OscillatorNode | null = null;
  private osc2: OscillatorNode | null = null;
  private gain: GainNode | null = null;
  private analyser: AnalyserNode | null = null;
  private dataArray: any = new Uint8Array(0);
  public isRunning: boolean = false;
  public frequency: number = 110;

  constructor() {}

  public toggle(): boolean {
    if (this.isRunning) {
      this.stop();
      return false;
    } else {
      this.start();
      return true;
    }
  }

  public start() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      this.ctx = new AudioCtx();
    }
    if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }

    this.analyser = this.ctx.createAnalyser();
    this.analyser.fftSize = 128;
    this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);

    this.gain = this.ctx.createGain();
    this.gain.gain.value = 0.15;

    // Harmonic dual oscillator for rich Chladni resonance
    this.osc1 = this.ctx.createOscillator();
    this.osc1.type = 'sine';
    this.osc1.frequency.setValueAtTime(this.frequency, this.ctx.currentTime);

    this.osc2 = this.ctx.createOscillator();
    this.osc2.type = 'triangle';
    this.osc2.frequency.setValueAtTime(this.frequency * 1.5, this.ctx.currentTime); // Perfect fifth harmonic

    this.osc1.connect(this.gain);
    this.osc2.connect(this.gain);
    this.gain.connect(this.analyser);
    this.analyser.connect(this.ctx.destination);

    this.osc1.start();
    this.osc2.start();
    this.isRunning = true;
  }

  public stop() {
    if (this.osc1) { this.osc1.stop(); this.osc1.disconnect(); }
    if (this.osc2) { this.osc2.stop(); this.osc2.disconnect(); }
    this.isRunning = false;
  }

  public setFrequency(freq: number) {
    this.frequency = freq;
    if (this.ctx && this.osc1 && this.osc2) {
      this.osc1.frequency.setTargetAtTime(freq, this.ctx.currentTime, 0.05);
      this.osc2.frequency.setTargetAtTime(freq * 1.5, this.ctx.currentTime, 0.05);
    }
  }

  public triggerImpact() {
    if (this.ctx && this.gain) {
      this.gain.gain.setValueAtTime(0.5, this.ctx.currentTime);
      this.gain.gain.exponentialRampToValueAtTime(0.15, this.ctx.currentTime + 0.8);
    }
  }

  public getEnergy(): number {
    if (!this.isRunning || !this.analyser) return 0.0;
    (this.analyser as any).getByteFrequencyData(this.dataArray);
    let sum = 0;
    for (let i = 0; i < this.dataArray.length; i++) {
      sum += this.dataArray[i];
    }
    return sum / (this.dataArray.length * 255.0);
  }
}
