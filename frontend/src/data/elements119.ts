export interface Element119 {
  id: number;
  symbol: string;
  name: string;
  zone: 1 | 2 | 3 | 4 | 5;
  zoneName: string;
  density: number;      // g/cm³
  shearModulus: number; // GPa
  affinity: 'Lithic' | 'Thermal' | 'Tensile' | 'Seismic' | 'Null';
  color: string;
}

export const ZONES = [
  { id: 1, name: 'Crypt Sub-Piers (Compressive)', count: 42, color: '#3b82f6' },
  { id: 2, name: 'Bessemer Gantries (Thermal)', count: 28, color: '#ef4444' },
  { id: 3, name: 'Crossing Spire (Tensile)', count: 24, color: '#00e5ff' },
  { id: 4, name: 'Observatory Invar (Seismic)', count: 15, color: '#ffd700' },
  { id: 5, name: 'Obsidian Sump (Zero-Point)', count: 10, color: '#78350f' }
];

export const ELEMENTS_119: Element119[] = [];

// Zone 1: Crypt Sub-Piers (1 to 42)
const lithicNames = ['Basalt', 'Gneiss', 'Granite', 'Hematite', 'Dolomite', 'Gabbro', 'Peridotite', 'Schist', 'Slate', 'Andesite', 'Syenite', 'Diorite', 'Quartzite', 'Amphibolite', 'Eclogite', 'Serpentine', 'Rhyolite', 'Chert', 'Porphyry', 'Anorthosite', 'Migmatite', 'Phyllite', 'Dunite', 'Norite', 'Troctolite', 'Pyroxenite', 'Hornblendite', 'Monzonite', 'Granodiorite', 'Tonalite', 'Greisen', 'Skarn', 'Mylonite', 'Cataclasite', 'Flint', 'Jasper', 'Obsidianite', 'Tuff', 'Breccia', 'Lapis', 'Steatite', 'Gritstone'];
for (let i = 1; i <= 42; i++) {
  ELEMENTS_119.push({
    id: i,
    symbol: `Cr-${i.toString().padStart(2, '0')}`,
    name: `${lithicNames[(i - 1) % lithicNames.length]}-Anchor`,
    zone: 1,
    zoneName: 'Crypt Sub-Piers',
    density: parseFloat((2.6 + (i * 0.05)).toFixed(2)),
    shearModulus: 22 + (i % 25),
    affinity: 'Lithic',
    color: i % 2 === 0 ? '#3b82f6' : '#2563eb'
  });
}

// Zone 2: Bessemer Gantries (43 to 70)
const thermalNames = ['Pyre-Ferrite', 'Blast-Tungsten', 'Tuyere-Slag', 'Crucible-Carbon', 'Molten-Nickel', 'Bessemer-Billet', 'Spiegel-Manganese', 'Silico-Manganese', 'Phosphor-Bronze', 'Coke-Breeze', 'Anthracite-Clinker', 'Graphite-Electrode', 'Fluorspar-Flux', 'Alumina-Refractory', 'Magnesite-Brick', 'Chromite-Lining', 'Zircon-Sleeve', 'Silicon-Carbide', 'Titanium-Dibro', 'Cobalt-Stellite', 'Ferro-Vanadium', 'Moly-Steel', 'Inconel-Gantry', 'Hastelloy-Brace', 'Nimonic-Tuyere', 'Monel-Baffle', 'Kovar-Truss', 'Stellite-Grate'];
for (let i = 43; i <= 70; i++) {
  ELEMENTS_119.push({
    id: i,
    symbol: `Bs-${i.toString().padStart(2, '0')}`,
    name: thermalNames[(i - 43) % thermalNames.length],
    zone: 2,
    zoneName: 'Bessemer Gantries',
    density: parseFloat((5.5 + ((i - 43) * 0.12)).toFixed(2)),
    shearModulus: 65 + ((i - 43) * 2),
    affinity: 'Thermal',
    color: (i % 2 === 0) ? '#ef4444' : '#f97316'
  });
}

// Zone 3: Crossing Spire (71 to 94)
const tensileNames = ['Auric-Chord', 'Cyan-Tension', 'Aer-Titanium', 'Wind-Strut', 'Zephyr-Cable', 'Apex-Guywire', 'Harmonic-Stay', 'Spire-Truss', 'Vortex-Tendon', 'Resonant-Brace', 'Gale-Spars', 'Aero-Carbon', 'Sky-Beryllium', 'Breeze-Nitinol', 'Ether-Rib', 'Zenith-Cord', 'Nimbus-Wire', 'Stratus-Tie', 'Thermic-Rod', 'Cross-Halyard', 'Pinnacle-Stay', 'Vertex-Loop', 'Windward-Tendon', 'Leeward-Strap'];
for (let i = 71; i <= 94; i++) {
  ELEMENTS_119.push({
    id: i,
    symbol: `Sp-${i.toString().padStart(2, '0')}`,
    name: tensileNames[(i - 71) % tensileNames.length],
    zone: 3,
    zoneName: 'Crossing Spire',
    density: parseFloat((3.8 + ((i - 71) * 0.09)).toFixed(2)),
    shearModulus: 45 + ((i - 71) * 1.8),
    affinity: 'Tensile',
    color: (i % 2 === 0) ? '#00e5ff' : '#10b981'
  });
}

// Zone 4: Observatory Invar (95 to 109)
const seismicNames = ['Invar-Fulcrum', 'Telluric-Quartz', 'Astrolabe-Brass', 'Seismic-Pendulum', 'Biaxial-Gimbal', 'Zenith-Pivot', 'Meridian-Prism', 'Chronos-Hairspring', 'Nodal-Bearing', 'Torsion-Filament', 'Horizon-Level', 'Astro-Invar', 'Declination-Pin', 'Azimuth-Trunnion', 'Ephemeris-Rotor'];
for (let i = 95; i <= 109; i++) {
  ELEMENTS_119.push({
    id: i,
    symbol: `Ob-${i.toString().padStart(2, '0')}`,
    name: seismicNames[(i - 95) % seismicNames.length],
    zone: 4,
    zoneName: 'Observatory Invar',
    density: parseFloat((8.1 + ((i - 95) * 0.11)).toFixed(2)),
    shearModulus: 75 + ((i - 95) * 3),
    affinity: 'Seismic',
    color: (i % 2 === 0) ? '#ffd700' : '#eab308'
  });
}

// Zone 5: Obsidian Sump (110 to 119)
const nullNames = ['Obsidian-Bedrock', 'Vitreous-Null', 'Zero-Basin', 'Void-Slab', 'Damping-Basalt', 'Grounding-Pelt', 'Static-Obsidian', 'Entropy-Sump', 'Null-Footing', 'Abyssal-Datum'];
for (let i = 110; i <= 119; i++) {
  ELEMENTS_119.push({
    id: i,
    symbol: `Nu-${i.toString().padStart(2, '0')}`,
    name: nullNames[(i - 110) % nullNames.length],
    zone: 5,
    zoneName: 'Obsidian Sump',
    density: parseFloat((2.8 + ((i - 110) * 0.04)).toFixed(2)),
    shearModulus: 18 + ((i - 110) * 1.2),
    affinity: 'Null',
    color: '#78350f'
  });
}
