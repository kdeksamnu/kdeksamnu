import * as THREE from 'three';

export const SomaticDualLumenShader = {
  uniforms: {
    uTime: { value: 0.0 },
    uResolution: { value: new THREE.Vector2(window.innerWidth, window.innerHeight) },
    uLumenCyan: { value: 1.4 },  // Psi: Ocular/structural verified intent
    uLumenGold: { value: 1.6 },  // Theta: Kinetic energy / speech cadence
    uScarIntensity: { value: 0.8 },
    uDialetheicTension: { value: 0.0 }, // C4 tension glow
    uLightDir: { value: new THREE.Vector3(0.5, 1.0, 0.8).normalize() }
  },
  vertexShader: `
    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vWorldPos;

    void main() {
      vUv = uv;
      vec4 wPos = modelMatrix * vec4(position, 1.0);
      vNormal = normalize(normalMatrix * normal);
      vWorldPos = wPos.xyz;
      gl_Position = projectionMatrix * viewMatrix * wPos;
    }
  `,
  fragmentShader: `
    uniform float uTime;
    uniform vec2 uResolution;
    uniform float uLumenCyan;
    uniform float uLumenGold;
    uniform float uScarIntensity;
    uniform float uDialetheicTension;
    uniform vec3 uLightDir;

    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vWorldPos;

    // Normalized 2x2 Bayer Threshold Matrix: M2 = 1/4 * [[0, 2],]
    float bayer2(vec2 p) {
      int x = int(mod(p.x, 2.0));
      int y = int(mod(p.y, 2.0));
      if (x == 0 && y == 0) return 0.0 / 4.0;
      if (x == 1 && y == 0) return 2.0 / 4.0;
      if (x == 0 && y == 1) return 3.0 / 4.0;
      return 1.0 / 4.0;
    }

    void main() {
      vec3 N = normalize(vNormal);
      vec3 L = normalize(uLightDir);
      float NdotL = max(dot(N, L), 0.0);
      float fresnel = pow(1.0 - max(abs(N.z), 0.0), 3.0);

      // 1.5 Hz Micro-Saccade Jitter (Sub-pixel temporal oscillation)
      vec2 jitter = vec2(sin(uTime * 9.42477), cos(uTime * 9.42477)) * 0.45;
      vec2 screenCoord = gl_FragCoord.xy + jitter;

      // Channel Split: Psi Ocular Cyan & Theta Kinetic Gold
      vec3 psiCyan = vec3(0.0, 0.9, 1.0) * uLumenCyan * NdotL;
      vec3 thetaGold = vec3(1.0, 0.84, 0.0) * uLumenGold * pow(NdotL, 2.0);

      // Layer 11 Kintsugi Gold Scars
      float crack = abs(sin(vWorldPos.y * 6.0 + sin(vWorldPos.x * 6.0)));
      float scarMask = 1.0 - smoothstep(0.0, 0.09, crack);
      vec3 kintsugi = vec3(1.0, 0.85, 0.2) * scarMask * uScarIntensity * 3.0;

      // C4 Dialetheic Tension Glow (Red/Violet flash)
      vec3 tensionGlow = mix(vec3(0.9, 0.1, 0.2), vec3(0.6, 0.1, 0.9), sin(uTime * 6.0) * 0.5 + 0.5);
      vec3 totalRadiance = psiCyan + thetaGold + kintsugi + tensionGlow * uDialetheicTension;

      // 2x2 Bayer Quantization
      float bayer = bayer2(screenCoord);
      float intensity = dot(totalRadiance, vec3(0.299, 0.587, 0.114));
      float dithered = step(bayer, intensity);

      vec3 finalCol = mix(vec3(0.02, 0.025, 0.04), totalRadiance, dithered);
      finalCol += psiCyan * fresnel * 0.4;

      gl_FragColor = vec4(finalCol, 1.0);
    }
  `
};
