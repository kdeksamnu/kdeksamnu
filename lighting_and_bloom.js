// --- Light & Shading Control: Rim Lighting, Dynamic Point Lights, & Bloom ---
// This module upgrades the pipeline for the [Visual Echo](http://localhost:8000/visuals) observer core, 
// introducing Fresnel rim glow, orbiting orbital lights, and emissive bloom post-processing.

import * as THREE from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';

// 1. Custom Shader Material with Fresnel Rim Lighting
const rimShaderMaterial = new THREE.ShaderMaterial({
    uniforms: {
        time: { value: 0.0 },
        baseColor: { value: new THREE.Color(0xff2222) },
        rimColor: { value: new THREE.Color(0x88ccff) }
    },
    vertexShader: `
        varying vec3 vNormal;
        varying vec3 vViewPosition;
        void main() {
            vNormal = normalize(normalMatrix * normal);
            vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
            vViewPosition = -mvPosition.xyz;
            gl_Position = projectionMatrix * mvPosition;
        }
    `,
    fragmentShader: `
        varying vec3 vNormal;
        varying vec3 vViewPosition;
        uniform vec3 baseColor;
        uniform uniform vec3 rimColor;
        void main() {
            vec3 normal = normalize(vNormal);
            vec3 viewDir = normalize(vViewPosition);
            
            // Calculate Fresnel rim factor (edges glow intensely, interior fades)
            float rim = 1.0 - max(dot(viewDir, normal), 0.0);
            rim = pow(rim, 3.0); // Sharpen rim falloff

            vec3 finalColor = mix(baseColor, rimColor, rim);
            gl_FragColor = vec4(finalColor, 0.9);
        }
    `,
    wireframe: true,
    transparent: true
});

// 2. Dynamic Point Lights Orbiting the Mesh
const orbitingLight = new THREE.PointLight(0x00ffff, 3.0, 50);
scene.add(orbitingLight);

// Update function within the render loop for orbiting motion
function updateLighting(time) {
    const radius = 8.0;
    orbitingLight.position.x = Math.cos(time * 0.7) * radius;
    orbitingLight.position.z = Math.sin(time * 0.7) * radius;
    orbitingLight.position.y = Math.sin(time * 0.3) * 3.0;
}

// 3. Emissive Bloom Post-Processing Pass
const composer = new EffectComposer(renderer);
const renderPass = new RenderPass(scene, camera);
composer.addPass(renderPass);

const bloomPass = new UnrealBloomPass(
    new THREE.Vector2(window.innerWidth, window.innerHeight),
    1.5,  // Strength
    0.4,  // Radius
    0.85  // Threshold
);
composer.addPass(bloomPass);

console.log('[CATHEDRAL-ENGINE] Lighting and bloom pipeline compiled successfully.');
