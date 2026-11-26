import * as THREE from 'three';

export const ReactorShader = {
  uniforms: {
    uTime: { value: 0.0 },
    uPhase: { value: 1 },
    uColorA: { value: new THREE.Color(0x00e5ff) },
    uColorB: { value: new THREE.Color(0xffd700) },
    uMixRatio: { value: 0.5 },
    uTemperature: { value: 1200.0 },
    uContainment: { value: 0.85 },
    uTurbulence: { value: 1.0 },
    uPulseEnergy: { value: 0.0 },
    uDitherScale: { value: 2.0 },
    uMagicAngle: { value: 0.0 },     // 0.0 -> 1.0 (cancels shear at 1.0)
    uScarIntensity: { value: 0.0 },   // Harmonic scar glowing veins
    uCymaticsFreq: { value: 0.0 },    // Chladni nodal standing waves
    uQuarantine: { value: 0.0 },      // Stasis hazard barrier
    uLightDir: { value: new THREE.Vector3(0.5, 1.0, 0.8).normalize() }
  },
  vertexShader: `
    uniform float uTime;
    uniform int uPhase;
    uniform float uTemperature;
    uniform float uContainment;
    uniform float uTurbulence;
    uniform float uPulseEnergy;
    uniform float uMagicAngle;
    uniform float uCymaticsFreq;

    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vWorldPos;
    varying float vActivity;
    varying vec3 vLocalPos;

    void main() {
      vUv = uv;
      vec3 pos = position;
      vLocalPos = pos;
      vec3 N = normalize(normal);

      float thermalEnergy = clamp(uTemperature / 2500.0, 0.05, 3.0);
      float t = uTime * (0.8 + thermalEnergy * 0.8);
      float displacement = 0.0;

      // Base phase displacements
      if (uPhase == 0) {
        float facet = floor(sin(pos.x * 2.0) * sin(pos.y * 2.0) * sin(pos.z * 2.0) * 4.0) / 4.0;
        displacement = facet * 0.35;
      } else if (uPhase == 1) {
        float wave1 = sin(pos.x * 1.5 + t * 2.0) * cos(pos.z * 1.5 + t * 1.8);
        float wave2 = sin(pos.y * 3.0 - t * 2.5) * 0.4;
        displacement = (wave1 + wave2) * 0.8 * thermalEnergy;
      } else if (uPhase == 2) {
        float arc = sin(pos.y * 5.0 * uTurbulence + t * 5.0) * cos(pos.x * 5.0 * uTurbulence - t * 4.0);
        float breach = (1.0 - uContainment) * sin(t * 8.0) * 1.5;
        displacement = (arc + breach) * 0.9 * thermalEnergy;
      } else if (uPhase == 3) {
        float r = length(pos);
        displacement = sin(r * 4.0 - t * 3.0) * cos(t * 2.0) * 1.2 * thermalEnergy;
      }

      // EXPERIMENT 1: MAGIC-ANGLE CANCELLATION (P2 tensorial damping)
      if (uMagicAngle > 0.01) {
        float theta = 0.9553; // 54.7356 degrees in radians
        float P2 = 0.5 * (3.0 * pow(cos(theta), 2.0) - 1.0); // cancels to ~0
        displacement = mix(displacement, P2 * sin(length(pos.xz) * 3.0), uMagicAngle);
      }

      // EXPERIMENT 3: CYMATICS NODAL FREQUENCY
      if (uCymaticsFreq > 0.1) {
        float chladni = sin(pos.x * uCymaticsFreq) * sin(pos.y * uCymaticsFreq) * sin(pos.z * uCymaticsFreq);
        displacement += chladni * 0.7;
      }

      displacement += uPulseEnergy * sin(length(pos) * 8.0 - uTime * 15.0) * 0.8;
      pos += N * displacement;

      vec4 wPos = modelMatrix * vec4(pos, 1.0);
      vNormal = normalize(normalMatrix * N);
      vWorldPos = wPos.xyz;
      vActivity = abs(displacement);

      gl_Position = projectionMatrix * viewMatrix * wPos;
    }
  `,
  fragmentShader: `
    uniform float uTime;
    uniform int uPhase;
    uniform vec3 uColorA;
    uniform vec3 uColorB;
    uniform float uMixRatio;
    uniform float uTemperature;
    uniform float uDitherScale;
    uniform vec3 uLightDir;
    uniform float uPulseEnergy;
    uniform float uScarIntensity;
    uniform float uQuarantine;

    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vWorldPos;
    varying float vActivity;
    varying vec3 vLocalPos;

    float bayer4(vec2 p) {
      int x = int(mod(p.x, 4.0));
      int y = int(mod(p.y, 4.0));
      int i = x + y * 4;
      if (i == 0) return 0.0;
      if (i == 1) return 8.0/16.0;
      if (i == 2) return 2.0/16.0;
      if (i == 3) return 10.0/16.0;
      if (i == 4) return 12.0/16.0;
      if (i == 5) return 4.0/16.0;
      if (i == 6) return 14.0/16.0;
      if (i == 7) return 6.0/16.0;
      if (i == 8) return 3.0/16.0;
      if (i == 9) return 11.0/16.0;
      if (i == 10) return 1.0/16.0;
      if (i == 11) return 9.0/16.0;
      if (i == 12) return 15.0/16.0;
      if (i == 13) return 7.0/16.0;
      if (i == 14) return 13.0/16.0;
      return 5.0/16.0;
    }

    void main() {
      vec3 N = normalize(vNormal);
      vec3 L = normalize(uLightDir);
      float NdotL = max(dot(N, L), 0.0);
      float fresnel = pow(1.0 - max(abs(N.z), 0.0), 2.8);

      vec3 elementCol = mix(uColorA, uColorB, uMixRatio);
      float thermalGlow = clamp((uTemperature - 800.0) / 2500.0, 0.0, 1.0);
      vec3 blackbody = mix(vec3(0.0), vec3(1.0, 0.45, 0.1), thermalGlow);

      vec3 coreColor = elementCol + blackbody * 0.6;

      if (uPhase == 1) {
        coreColor = mix(coreColor * 0.5, elementCol, fresnel) + vec3(fresnel * 0.4);
      } else if (uPhase == 2) {
        coreColor += vec3(0.4, 0.2, 1.0) * pow(vActivity, 1.5) * 2.0 + vec3(1.0) * pow(fresnel, 3.0) * 1.2;
      } else if (uPhase == 3) {
        vec3 rainbow = 0.5 + 0.5 * cos(6.28318 * (fresnel * 1.5 + vec3(0.0, 0.33, 0.67) + uTime * 0.2));
        coreColor = mix(coreColor, rainbow, 0.8) + vec3(fresnel * 0.6);
      }

      // EXPERIMENT 2: HARMONIC SCAR CRACK VEINS (Glowing gold/violet crystalline fault lines)
      if (uScarIntensity > 0.01) {
        float scarCrack = abs(sin(vLocalPos.x * 6.0 + sin(vLocalPos.y * 6.0)) * cos(vLocalPos.z * 6.0));
        float scarVein = 1.0 - smoothstep(0.0, 0.08, scarCrack);
        vec3 scarColor = mix(vec3(1.0, 0.84, 0.0), vec3(0.7, 0.2, 1.0), sin(vLocalPos.y * 4.0) * 0.5 + 0.5);
        coreColor = mix(coreColor, scarColor * 2.2, scarVein * uScarIntensity);
      }

      // EXPERIMENT 5: QUARANTINE STASIS HAZARD BARS
      if (uQuarantine > 0.01) {
        float hazard = step(0.5, fract((vWorldPos.y + vWorldPos.x) * 0.5 + uTime * 0.5));
        vec3 stasisCol = mix(vec3(0.05, 0.05, 0.08), vec3(1.0, 0.6, 0.0), hazard);
        coreColor = mix(coreColor, stasisCol, uQuarantine * 0.85);
      }

      coreColor += vec3(uPulseEnergy * 1.5);

      float chiaroscuro = smoothstep(0.25, 0.45, NdotL + thermalGlow * 0.3);
      vec2 screenCoord = gl_FragCoord.xy / max(uDitherScale, 1.0);
      float bayer = bayer4(screenCoord);
      float dithered = mix(chiaroscuro, step(bayer, chiaroscuro), 0.75);

      vec3 finalColor = max(coreColor * dithered, coreColor * 0.15);
      gl_FragColor = vec4(finalColor, 1.0);
    }
  `
};
