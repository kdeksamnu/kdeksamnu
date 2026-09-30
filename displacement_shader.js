// Assuming 'geometry' is your sphere buffer geometry and 'clock' is a Three.js Clock
const positionAttribute = geometry.attributes.position;
const vertex = new THREE.Vector3();
const time = clock.getElapsedTime();

for (let i = 0; i < positionAttribute.count; i++) {
    vertex.fromBufferAttribute(positionAttribute, i);

    // Normalize to get the vertex direction from the sphere center, then scale with noise
    const normal = vertex.clone().normalize();
    
    // Replace with your noise function of choice (e.g., Simplex / Perlin noise)
    // Multiplying coordinates by frequency and adding time creates organic motion
    const noise = simplex.noise3D(
        vertex.x * 0.05 + time * 0.5, 
        vertex.y * 0.05 + time * 0.5, 
        vertex.z * 0.05 + time * 0.5
    );

    // Apply displacement along the vertex normal
    const displacement = 1.0 + noise * 0.15; // 0.15 controls deformation amplitude
    vertex.copy(normal).multiplyScalar(initialRadius * displacement);

    positionAttribute.setXYZ(i, vertex.x, vertex.y, vertex.z);
}

positionAttribute.needsUpdate = true; // Essential to signal GPU buffer updates
