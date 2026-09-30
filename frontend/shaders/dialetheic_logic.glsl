// --- THE DIALETHEIC LOGIC GATE & BOUNDARY CLAMP ---

uniform float u_time;

vec4 apply_dialetheic_interference(vec3 base_color, float raw_state_encoded, float raw_thermal) {
    // 1. THE BOUNDARY CLAMP: Prevent GPU execution divergence
    float state_encoded = clamp(raw_state_encoded, 0.0, 1.0);
    float thermal = clamp(raw_thermal, 0.0, 1.0);

    // 2. THE DIALETHEIC FRACTURE (BOTH > 0.8)
    if (state_encoded > 0.8) {
        float split = thermal * 0.15;
        float flicker = sin(u_time * 8.0) * 0.5 + 0.5;
        return vec4(
            base_color.r + (split * flicker), 
            base_color.g - (split * 0.5), 
            base_color.b - (split * (1.0 - flicker)), 
            1.0
        );
    } 
    // 3. CONSTRUCTIVE RESONANCE (TRUE > 0.5)
    else if (state_encoded > 0.5) {
        return vec4(base_color * 1.2, 1.0);
    } 
    // 4. DESTRUCTIVE DAMPENING (FALSE > 0.2)
    else if (state_encoded > 0.2) {
        return vec4(base_color * 0.4, 0.8);
    } 
    // 5. THE GROUNDING VOID (NEITHER)
    else {
        return vec4(0.02, 0.02, 0.05, 0.0); 
    }
}
