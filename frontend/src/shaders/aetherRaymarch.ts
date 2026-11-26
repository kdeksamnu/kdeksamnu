import * as THREE from 'three';

export const AetherRaymarchShader = {
  uniforms: {
    uTime: { value: 0.0 },
    uResolution: { value: new THREE.Vector2(window.innerWidth, window.innerHeight) },
    uMouse: { value: new THREE.Vector2(0.5, 0.5) },
    uGoldBleed: { value: 0.65 },
    uPrismRefract: { value: 1.15 }
  },
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = vec4(position.xy, 0.0, 1.0);
    }
  `,
  fragmentShader: `
    uniform float uTime;
    uniform vec2 uResolution;
    uniform vec2 uMouse;
    uniform float uGoldBleed;
    uniform float uPrismRefract;
    varying vec2 vUv;

    // SDF Primitive Combinators
    float sdBox(vec3 p, vec3 b) {
      vec3 q = abs(p) - b;
      return length(max(q, 0.0)) + min(max(q.x, max(q.y, q.z)), 0.0);
    }

    float sdOctahedron(vec3 p, float s) {
      p = abs(p);
      return (p.x + p.y + p.z - s) * 0.57735027;
    }

    // Scene Distance Field: Infinite Obsidian Corridor + Floating Prism
    float map(vec3 p) {
      // Repetition along Z-axis for infinite brutalist colonnade
      vec3 q = p;
      q.z = mod(q.z + 5.0, 10.0) - 5.0;

      // Monolithic pillars
      float pillarL = sdBox(q - vec3(-7.5, 0.0, 0.0), vec3(1.2, 14.0, 1.2));
      float pillarR = sdBox(q - vec3(7.5, 0.0, 0.0), vec3(1.2, 14.0, 1.2));

      // Floor and vaulted ceiling
      float floorD = p.y + 6.0;
      float ceilingD = -(p.y - 12.0);

      // Central Levitating Refractive Prism
      vec3 prismPos = p - vec3(0.0, 0.5 + sin(uTime * 1.2) * 0.4, p.z);
      float prism = sdOctahedron(prismPos, 3.2);

      return min(min(pillarL, pillarR), min(min(floorD, ceilingD), prism));
    }

    vec3 calcNormal(vec3 p) {
      float h = 0.001;
      vec2 k = vec2(1, -1);
      return normalize(
        k.xyy * map(p + k.xyy * h) +
        k.yyx * map(p + k.yyx * h) +
        k.yxy * map(p + k.yxy * h) +
        k.xxx * map(p + k.xxx * h)
      );
    }

    void main() {
      vec2 uv = (gl_FragCoord.xy - 0.5 * uResolution.xy) / uResolution.y;
      
      // Camera ray with slight mouse tilt
      vec3 ro = vec3(0.0, 0.5, uTime * 2.5);
      vec2 look = (uMouse - 0.5) * 0.35;
      vec3 rd = normalize(vec3(uv + look, 1.2));

      float t = 0.0;
      for (int i = 0; i < 75; i++) {
        vec3 p = ro + rd * t;
        float d = map(p);
        if (d < 0.002 || t > 70.0) break;
        t += d * 0.75;
      }

      // Obsidian Void Background
      vec3 col = vec3(0.02, 0.02, 0.035);

      if (t < 70.0) {
        vec3 p = ro + rd * t;
        vec3 n = calcNormal(p);

        // Volumetric Distance Fog
        float fog = 1.0 - exp(-t * 0.028);

        // Chiaroscuro key light
        vec3 lightDir = normalize(vec3(0.4, 0.8, 0.5));
        float diff = max(dot(n, lightDir), 0.0);
        float spec = pow(max(dot(reflect(-lightDir, n), -rd), 0.0), 32.0);

        // "The Golden Bleed": Warm molten veins pulsing through cracks in the stone
        float crack = abs(sin(p.z * 0.8 - uTime * 2.0) * cos(p.x * 0.8) + sin(p.y * 1.2));
        float vein = 1.0 - smoothstep(0.0, 0.12, crack);
        vec3 goldVein = vec3(1.0, 0.82, 0.22) * vein * uGoldBleed * 3.5;

        // Base obsidian brutalist tone
        vec3 obsidian = vec3(0.04, 0.04, 0.06) + diff * vec3(0.12) + spec * vec3(0.6);
        obsidian += goldVein;

        // Refractive glass prism tint
        if (sdOctahedron(p - vec3(0.0, 0.5 + sin(uTime * 1.2) * 0.4, p.z), 3.3) < 0.1) {
          float fresnel = pow(1.0 - max(dot(n, -rd), 0.0), 3.0);
          obsidian = mix(vec3(0.01, 0.04, 0.06), vec3(0.0, 0.9, 1.0), fresnel * uPrismRefract);
          obsidian += goldVein * 0.8;
        }

        col = mix(obsidian, vec3(0.01, 0.01, 0.02), fog);
      }

      gl_FragColor = vec4(col, 1.0);
    }
  `
};
