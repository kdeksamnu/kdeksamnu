import * as THREE from 'three';

export const DitherShader = {
  uniforms: {
    uTime: { value: 0.0 },
    uMode: { value: 0 }, // 0=Strata, 1=Liquid, 2=Plasma, 3=Spectral
    uColor: { value: new THREE.Color(0x00e5ff) },
    uSecondaryColor: { value: new THREE.Color(0xffd700) },
    uLumen: { value: 1.6 },
    uDitherScale: { value: 2.0 },
    uChiaroscuroThreshold: { value: 0.35 },
    uDitherMix: { value: 0.75 },
    uLightDir: { value: new THREE.Vector3(0.5, 1.0, 0.8).normalize() },
    uWaveFreq: { value: 0.35 },
    uWaveAmp: { value: 1.2 },
    uWaveSpeed: { value: 1.8 },
    uTurbulence: { value: 0.8 },
    uIridescence: { value: 0.85 }
  },
  vertexShader: `
    uniform float uTime;
    uniform int uMode;
    uniform float uWaveFreq;
    uniform float uWaveAmp;
    uniform float uWaveSpeed;
    uniform float uTurbulence;

    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vWorldPos;
    varying float vDisplacement;

    void main() {
      vUv = uv;
      vec3 pos = position;

      #ifdef USE_INSTANCING
        vec4 wPos = modelMatrix * instanceMatrix * vec4(pos, 1.0);
        vNormal = normalize(mat3(modelMatrix * instanceMatrix) * normal);
      #else
        vec4 wPos = modelMatrix * vec4(pos, 1.0);
        vNormal = normalize(normalMatrix * normal);
      #endif

      float disp = 0.0;
      float t = uTime * uWaveSpeed;

      // 1. LIQUID MODE: Harmonic multi-wave superposition
      if (uMode == 1) {
        float wave1 = sin(wPos.x * uWaveFreq + t) * cos(wPos.z * uWaveFreq + t * 0.8);
        float wave2 = sin((wPos.x + wPos.z) * uWaveFreq * 1.5 - t * 1.2) * 0.5;
        disp = (wave1 + wave2) * uWaveAmp;
        wPos.y += disp;
      }
      // 2. PLASMA MODE: Volumetric breathing & turbulent pulse
      else if (uMode == 2) {
        float pulse = sin(length(wPos.xz) * uWaveFreq - t * 2.0);
        float jitter = sin(wPos.y * uTurbulence * 2.0 + t * 3.0) * cos(wPos.x * uTurbulence * 2.0 - t * 2.0);
        disp = (pulse + jitter * 0.6) * uWaveAmp;
        wPos.xyz += vNormal * disp * 0.4;
      }
      // 3. SPECTRAL MODE: Radial ripple & chromatic dilation
      else if (uMode == 3) {
        float r = length(wPos.xz);
        disp = sin(r * uWaveFreq - t * 1.5) * uWaveAmp;
        wPos.y += disp;
      }

      vDisplacement = disp;
      vWorldPos = wPos.xyz;
      gl_Position = projectionMatrix * viewMatrix * wPos;
    }
  `,
  fragmentShader: `
    uniform float uTime;
    uniform int uMode;
    uniform vec3 uColor;
    uniform vec3 uSecondaryColor;
    uniform float uLumen;
    uniform float uDitherScale;
    uniform float uChiaroscuroThreshold;
    uniform float uDitherMix;
    uniform vec3 uLightDir;
    uniform float uTurbulence;
    uniform float uIridescence;

    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vWorldPos;
    varying float vDisplacement;

    float getBayer4(vec2 p) {
      int x = int(mod(p.x, 4.0));
      int y = int(mod(p.y, 4.0));
      int idx = x + y * 4;
      if (idx == 0) return 0.0;
      if (idx == 1) return 8.0 / 16.0;
      if (idx == 2) return 2.0 / 16.0;
      if (idx == 3) return 10.0 / 16.0;
      if (idx == 4) return 12.0 / 16.0;
      if (idx == 5) return 4.0 / 16.0;
      if (idx == 6) return 14.0 / 16.0;
      if (idx == 7) return 6.0 / 16.0;
      if (idx == 8) return 3.0 / 16.0;
      if (idx == 9) return 11.0 / 16.0;
      if (idx == 10) return 1.0 / 16.0;
      if (idx == 11) return 9.0 / 16.0;
      if (idx == 12) return 15.0 / 16.0;
      if (idx == 13) return 7.0 / 16.0;
      if (idx == 14) return 13.0 / 16.0;
      return 5.0 / 16.0;
    }

    // Cosine spectral rainbow palette
    vec3 spectralPalette(float t) {
      vec3 a = vec3(0.5, 0.5, 0.5);
      vec3 b = vec3(0.5, 0.5, 0.5);
      vec3 c = vec3(1.0, 1.0, 1.0);
      vec3 d = vec3(0.0, 0.33, 0.67);
      return a + b * cos(6.28318 * (c * t + d));
    }

    void main() {
      vec3 N = normalize(vNormal);
      vec3 L = normalize(uLightDir);
      float NdotL = max(dot(N, L), 0.0);
      float fresnel = pow(1.0 - max(abs(N.z), 0.0), 3.0);

      vec3 baseCol = uColor;

      // MODE 1: LIQUID (Viscous depth shading + crest highlight)
      if (uMode == 1) {
        float fluidDepth = clamp((vDisplacement + 1.5) / 3.0, 0.0, 1.0);
        baseCol = mix(uColor * 0.4, uSecondaryColor, fluidDepth);
        baseCol += vec3(fresnel * 0.6); // Liquid caustic crests
      }
      // MODE 2: PLASMA (Multi-phase turbulent corona)
      else if (uMode == 2) {
        float pNoise = sin(vWorldPos.x * uTurbulence + uTime * 2.0)
                     + sin(vWorldPos.y * uTurbulence - uTime * 3.0)
                     + sin(vWorldPos.z * uTurbulence + uTime * 1.5);
        float plasmaMix = 0.5 + 0.5 * sin(pNoise * 2.5 + uTime * 3.5);
        baseCol = mix(uColor, uSecondaryColor, plasmaMix);
        baseCol += vec3(0.8, 0.3, 1.0) * pow(fresnel, 2.0) * 1.5; // Plasma corona arc
      }
      // MODE 3: SPECTRAL (Thin-film prismatic dispersion)
      else if (uMode == 3) {
        float shift = fresnel * 1.8 + vDisplacement * 0.3 + uTime * 0.15;
        vec3 rainbow = spectralPalette(shift);
        baseCol = mix(uColor, rainbow, uIridescence);
        baseCol = mix(baseCol, uSecondaryColor, fresnel * 0.5);
      }

      // Chiaroscuro Lighting Calculation
      float rawDiff = NdotL * uLumen;
      float chiaroscuro = smoothstep(uChiaroscuroThreshold - 0.08, uChiaroscuroThreshold + 0.08, rawDiff);

      // Bayer Dithering
      vec2 screenCoord = gl_FragCoord.xy / max(uDitherScale, 1.0);
      float bayerVal = getBayer4(screenCoord);
      float ditherStep = step(bayerVal, chiaroscuro);
      float finalShading = mix(chiaroscuro, ditherStep, uDitherMix);

      vec3 shadowFloor = baseCol * 0.12;
      vec3 litColor = baseCol * finalShading;
      gl_FragColor = vec4(max(litColor, shadowFloor), 1.0);
    }
  `
};
