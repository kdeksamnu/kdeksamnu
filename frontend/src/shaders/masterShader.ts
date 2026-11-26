import * as THREE from 'three';

export const GlobalUniforms = {
  uTime: { value: 0.0 },
  uResolution: { value: new THREE.Vector2(window.innerWidth, window.innerHeight) },
  uColorPrimary: { value: new THREE.Color(0x00e5ff) },
  uColorSecondary: { value: new THREE.Color(0xffd700) },
  uColorShadow: { value: new THREE.Color(0x07080d) },
  uChromaticShift: { value: 0.75 },
  uBayerScale: { value: 2.0 },
  uDitherStrength: { value: 0.75 },
  uNoiseScale: { value: 3.5 },
  uRoughness: { value: 0.35 },
  uMetallic: { value: 0.8 },
  uCrackDensity: { value: 2.2 },
  uVeinGlow: { value: 1.6 },
  uLumenExposure: { value: 1.6 },
  uChiaroscuroCut: { value: 0.35 },
  uShadowFloor: { value: 0.12 },
  uFresnelPower: { value: 3.0 },
  uLightDir: { value: new THREE.Vector3(0.5, 1.0, 0.8).normalize() }
};

export const CathedralMasterShader = {
  uniforms: GlobalUniforms,
  vertexShader: `
    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vWorldPos;
    void main() {
      vUv = uv;
      #ifdef USE_INSTANCING
        vec4 wPos = modelMatrix * instanceMatrix * vec4(position, 1.0);
        vNormal = normalize(mat3(modelMatrix * instanceMatrix) * normal);
      #else
        vec4 wPos = modelMatrix * vec4(position, 1.0);
        vNormal = normalize(normalMatrix * normal);
      #endif
      vWorldPos = wPos.xyz;
      gl_Position = projectionMatrix * viewMatrix * wPos;
    }
  `,
  fragmentShader: `
    uniform float uTime;
    uniform vec3 uColorPrimary;
    uniform vec3 uColorSecondary;
    uniform vec3 uColorShadow;
    uniform float uBayerScale;
    uniform float uDitherStrength;
    uniform float uLumenExposure;
    uniform float uChiaroscuroCut;
    uniform vec3 uLightDir;

    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vWorldPos;

    float bayer2(vec2 p) {
      int x = int(mod(p.x, 2.0));
      int y = int(mod(p.y, 2.0));
      if (x == 0 && y == 0) return 0.0;
      if (x == 1 && y == 0) return 0.5;
      if (x == 0 && y == 1) return 0.75;
      return 0.25;
    }

    void main() {
      vec3 N = normalize(vNormal);
      vec3 L = normalize(uLightDir);
      float diff = max(dot(N, L), 0.0) * uLumenExposure;
      float chiaroscuro = smoothstep(uChiaroscuroCut - 0.08, uChiaroscuroCut + 0.08, diff);
      float bayer = bayer2(gl_FragCoord.xy / max(uBayerScale, 1.0));
      float dithered = mix(chiaroscuro, step(bayer, chiaroscuro), uDitherStrength);

      vec3 col = mix(uColorShadow, uColorPrimary, dithered);
      gl_FragColor = vec4(col, 1.0);
    }
  `
};
