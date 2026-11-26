export class HauteCoutureDOM {
  public cursorDot: HTMLElement;
  public cursorRing: HTMLElement;
  public mouseX: number = 0;
  public mouseY: number = 0;
  public ringX: number = 0;
  public ringY: number = 0;

  constructor() {
    this.cursorDot = document.createElement('div');
    this.cursorRing = document.createElement('div');
    this.initCursorStyles();
    this.bindEvents();
  }

  private initCursorStyles() {
    // Center glowing gold point
    this.cursorDot.style.position = 'fixed';
    this.cursorDot.style.width = '6px';
    this.cursorDot.style.height = '6px';
    this.cursorDot.style.background = '#ffd700';
    this.cursorDot.style.boxShadow = '0 0 10px #ffd700';
    this.cursorDot.style.borderRadius = '50%';
    this.cursorDot.style.pointerEvents = 'none';
    this.cursorDot.style.zIndex = '9999';
    this.cursorDot.style.transform = 'translate(-50%, -50%)';

    // Gravitational cyan ring reticle
    this.cursorRing.style.position = 'fixed';
    this.cursorRing.style.width = '34px';
    this.cursorRing.style.height = '34px';
    this.cursorRing.style.border = '1px solid rgba(0, 229, 255, 0.65)';
    this.cursorRing.style.borderRadius = '50%';
    this.cursorRing.style.pointerEvents = 'none';
    this.cursorRing.style.zIndex = '9998';
    this.cursorRing.style.transform = 'translate(-50%, -50%)';
    this.cursorRing.style.transition = 'width 0.2s, height 0.2s, border-color 0.2s';

    document.body.appendChild(this.cursorDot);
    document.body.appendChild(this.cursorRing);
  }

  private bindEvents() {
    window.addEventListener('mousemove', (e) => {
      this.mouseX = e.clientX;
      this.mouseY = e.clientY;
      this.cursorDot.style.left = `${this.mouseX}px`;
      this.cursorDot.style.top = `${this.mouseY}px`;
    });

    // Magnetic interaction warping when hovering clickable elements
    document.addEventListener('mouseover', (e) => {
      const target = e.target as HTMLElement;
      if (target && (target.tagName === 'BUTTON' || target.tagName === 'A' || target.tagName === 'INPUT')) {
        this.cursorRing.style.width = '48px';
        this.cursorRing.style.height = '48px';
        this.cursorRing.style.borderColor = '#ffd700';
      }
    });

    document.addEventListener('mouseout', (e) => {
      const target = e.target as HTMLElement;
      if (target && (target.tagName === 'BUTTON' || target.tagName === 'A' || target.tagName === 'INPUT')) {
        this.cursorRing.style.width = '34px';
        this.cursorRing.style.height = '34px';
        this.cursorRing.style.borderColor = 'rgba(0, 229, 255, 0.65)';
      }
    });
  }

  public update() {
    // Smooth magnetic interpolation (lagging fluid reticle)
    this.ringX += (this.mouseX - this.ringX) * 0.15;
    this.ringY += (this.mouseY - this.ringY) * 0.15;
    this.cursorRing.style.left = `${this.ringX}px`;
    this.cursorRing.style.top = `${this.ringY}px`;
  }
}
