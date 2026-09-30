// --- THE GLASS CATHEDRAL: FRAGMENT SHADER UNIFORMS ---

// 1. Structural Integrity [0.0, 1.0]
uniform float u_somatic_integrity; 

// 2. Normalized Thermal Load [0.0, 1.0] 
uniform float u_thermal_load; 

// 3. Dialetheic Velocity [0.0, 1.0]
uniform float u_dialetheic_velocity; 

// 4. Active Scars [0, N]
uniform float u_active_harmonic_scars; 

// 5. Spectral Phase [0.0, 2π]
uniform float u_spectral_phase; 

// 6. Time and Resolution for dynamic effects
uniform float u_time;
uniform vec2 u_resolution;

// --- TRANSFER FUNCTIONS ---

// Maps thermal load to chromatic aberration shift and IOR distortion
vec3 apply_thermal_distortion(vec3 base_color, vec2 uv) {
    float aberration_shift = u_thermal_load * u_dialetheic_velocity * 0.05;
    
    // Simulated texture sampling for aberration (placeholder for actual texture)
    float r = base_color.r + aberration_shift;
    float g = base_color.g;
    float b = base_color.b - aberration_shift;
    
    // Heat shimmer: distort UVs based on thermal load and time
    float shimmer = sin(uv.y * 20.0 + u_time * 2.0) * (u_thermal_load * 0.02);
    uv += vec2(shimmer);
    
    return vec3(r, g, b);
}

// Maps active scars to Voronoi fracture opacity
float apply_scar_fracture(vec2 uv) {
    if (u_active_harmonic_scars < 1.0) return 1.0; 
    
    float cell_size = 0.15 / (1.0 + u_active_harmonic_scars * 0.1);
    vec2 cell_id = floor(uv / cell_size);
    vec2 frag_coord = fract(uv / cell_size) - 0.5;
    float dist = length(frag_coord);
    
    float fracture_opacity = smoothstep(0.4, 0.45, dist) * (1.0 - u_somatic_integrity);
    return 1.0 - fracture_opacity;
}

void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution;
    vec3 base_color = vec3(0.9, 0.95, 1.0) * u_somatic_integrity;
    
    vec3 final_color = apply_thermal_distortion(base_color, uv);
    float fracture_mask = apply_scar_fracture(uv);
    
    gl_FragColor = vec4(final_color * fracture_mask, u_somatic_integrity);
}
