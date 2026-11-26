export class PaintBrushCursor {
  public cursorDot: HTMLElement;
  public cursorRing: HTMLElement;
  public brushQuill: HTMLElement;
  public mouseX: number = 0;
  public mouseY: number = 0;
  public brushSize: number = 18;
  public brushColor: string = '#00e5ff';
  public isPainting: boolean = false;

  private prevX: number = 0;
  private prevY: number = 0;
  private angle: number = 0;

  constructor() {
    this.cursorDot = document.createElement('div');
    this.cursorRing = document.createElement('div');
    this.brushQuill = document.createElement('div');

    this.initStyles();
    this.bindEvents();
  }

  private initStyles() {
    // Center Pigment Core
    this.cursorDot.style.position = 'fixed';
    this.cursorDot.style.width = '6px';
    this.cursorDot.style.height = '6px';
    this.cursorDot.style.background = this.brushColor;
    this.cursorDot.style.boxShadow = `0 0 10px ${this.brushColor}`;
    this.cursorDot.style.borderRadius = '50%';
    this.cursorDot.style.pointerEvents = 'none';
    this.cursorDot.style.zIndex = '9999';
    this.cursorDot.style.transform = 'translate(-50%, -50%)';

    // Outer Radius Ring (Shows Brush Size)
    this.cursorRing.style.position = 'fixed';
    this.cursorRing.style.width = `${this.brushSize * 2}px`;
    this.cursorRing.style.height = `${this.brushSize * 2}px`;
    this.cursorRing.style.border = `1px dashed ${this.brushColor}`;
    this.cursorRing.style.borderRadius = '50%';
    this.cursorRing.style.pointerEvents = 'none';
    this.cursorRing.style.zIndex = '9998';
    this.cursorRing.style.transform = 'translate(-50%, -50%)';
    this.cursorRing.style.transition = 'width 0.1s, height 0.1s, border-color 0.15s';

    // Dynamic Tilting Brush Tip
    this.brushQuill.style.position = 'fixed';
    this.brushQuill.style.width = '2px';
    this.brushQuill.style.height = '14px';
    this.brushQuill.style.background = 'linear-gradient(to top, #ffd700, transparent)';
    this.brushQuill.style.pointerEvents = 'none';
    this.brushQuill.style.zIndex = '9997';
    this.brushQuill.style.transformOrigin = 'bottom center';
    this.brushQuill.style.transform = 'translate(-50%, -100%)';

    document.body.appendChild(this.cursorDot);
    document.body.appendChild(this.cursorRing);
    document.body.appendChild(this.brushQuill);
  }

  public setColor(hex: string) {
    this.brushColor = hex;
    this.cursorDot.style.background = hex;
    this.cursorDot.style.boxShadow = `0 0 10px ${hex}`;
    this.cursorRing.style.borderColor = hex;
  }

  public setSize(size: number) {
    this.brushSize = size;
    this.cursorRing.style.width = `${size * 2}px`;
    this.cursorRing.style.height = `${size * 2}px`;
  }

  private bindEvents() {
    window.addEventListener('mousemove', (e) => {
      this.mouseX = e.clientX;
      this.mouseY = e.clientY;

      const dx = this.mouseX - this.prevX;
      const dy = this.mouseY - this.prevY;
      if (Math.abs(dx) > 0.5 || Math.abs(dy) > 0.5) {
        this.angle = Math.atan2(dy, dx) + Math.PI / 2;
      }
      this.prevX = this.mouseX;
      this.prevY = this.mouseY;

      this.cursorDot.style.left = `${this.mouseX}px`;
      this.cursorDot.style.top = `${this.mouseY}px`;

      this.cursorRing.style.left = `${this.mouseX}px`;
      this.cursorRing.style.top = `${this.mouseY}px`;

      this.brushQuill.style.left = `${this.mouseX}px`;
      this.brushQuill.style.top = `${this.mouseY}px`;
      this.brushQuill.style.transform = `translate(-50%, -100%) rotate(${this.angle}rad)`;
    });

    window.addEventListener('mousedown', () => { this.isPainting = true; });
    window.addEventListener('mouseup', () => { this.isPainting = false; });
  }

  public update() {}
}
