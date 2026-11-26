import * as THREE from 'three';

export const CinematicLensShader = {
  uniforms: {
    tDiffuse: { value: null },
    uAberration: { value: 0.0035 },
    uGrain: { value: 0.06 },
    uVignette: { value: 0.85 },
    uTime: { value: 0.0 }
  },
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = vec4(position.xy, 0.0, 1.0);
    }
  `,
  fragmentShader: `
    uniform sampler2D tDiffuse;
    uniform float uAberration;
    uniform float uGrain;
    uniform float uVignette;
    uniform float uTime;
    varying vec2 vUv;

    // ACES Filmic Tone Mapping Curve (Narkowicz 2015)
    vec3 acesFilmic(vec3 x) {
      float a = 2.51;
      float b = 0.03;
      float c = 2.43;
      float d = 0.59;
      float e = 0.14;
      return clamp((x * (a * x + b)) / (x * (c * x + d) + e), 0.0, 1.0);
    }

    void main() {
      vec2 dist = vUv - 0.5;
      
      // Directional Chromatic Aberration
      vec3 col;
      col.r = texture2D(tDiffuse, vUv + dist * uAberration).r;
      col.g = texture2D(tDiffuse, vUv).g;
      col.b = texture2D(tDiffuse, vUv - dist * uAberration).b;

      // Micro Surface Film Grain
      float noise = fract(sin(dot(vUv * (uTime + 1.0), vec2(12.9898, 78.233))) * 43758.5453);
      col += (noise - 0.5) * uGrain;

      // Soft Noir Cinematic Vignette
      float vig = clamp(16.0 * vUv.x * vUv.y * (1.0 - vUv.x) * (1.0 - vUv.y), 0.0, 1.0);
      col *= pow(vig, uVignette * 0.25);

      col = acesFilmic(col);
      gl_FragColor = vec4(col, 1.0);
    }
  `
};
