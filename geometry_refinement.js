// --- Tessellation & Subdivision Configuration ---
// Adjust these parameters during geometry initialization to increase wireframe density.
// Higher segment counts yield a denser vertex lattice, enabling ultra-fine grain deformation 
// and smooth curvature transitions across the Chaos-Subject manifold.

const radius = 5.0;
const widthSegments = 64; // Increased from default (e.g., 16 or 32) for high-density tessellation
const heightSegments = 64;

// Instantiate the refined buffer geometry
const highDensityGeometry = new THREE.SphereGeometry(radius, widthSegments, heightSegments);

// Optional: Apply subdivision modifier if using Three.js SubdivideModifier for non-uniform mesh refinement
// const modifier = new THREE.SubdivisionModifier(2);
// const subdividedGeometry = modifier.modify(highDensityGeometry);

console.log(`[CATHEDRAL-ENGINE] Geometry tessellation locked. Vertex count: ${highDensityGeometry.attributes.position.count}`);
