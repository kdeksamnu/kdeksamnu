// File: aurelia_panoptic_dither.gdshader
shader_type canvas_item;

// Uniforms mapped to Character State Vector C(t) and Somatic Stack
uniform float somatic_delta : hint_range(0.0, 3.0) = 1.5;
uniform float ash_archive_depth : hint_range(1.0, 6.0) = 5.0; // G05
uniform vec4 gold_emission_color : source_color = vec4(1.0, 0.84, 0.0, 1.0);
uniform vec4 cyan_lumen_color : source_color = vec4(0.0, 0.9, 1.0, 1.0);
uniform sampler2D lumen_flow_tex : hint_default_white;
uniform sampler2D scar_displacement_map : hint_default_black;

// Bayer 2x2 Matrix for Bio-Semantic Dithering
const float bayer2[4] = {
    0.0, 2.0,
    3.0, 1.0
};

void fragment() {
    vec2 uv = UV;
    
    // Sample base texture and structural deformation
    vec4 base_color = texture(TEXTURE, uv);
    vec4 scar_sample = texture(scar_displacement_map, uv);
    
    // Apply Bayer 2x2 threshold dither for panoptic aperture clipping (Layer 08)
    ivec2 int_uv = ivec2(FRAGCOORD.xy) % 2;
    int bayer_index = int_uv.y * 2 + int_uv.x;
    float threshold = (bayer2[bayer_index] + 0.5) / 4.0;
    
    // Lumen flow and dual-channel emission extraction (Layers 04 & 05)
    float lumen_flow = texture(lumen_flow_tex, uv + vec2(TIME * 0.1 * somatic_delta, 0.0)).r;
    vec3 emission_composite = (gold_emission_color.rgb * 0.6) + (cyan_lumen_color.rgb * lumen_flow * 1.4);
    
    // Harmonic scar integration (Layer 09): convert stress yield into load-bearing reinforcement
    if (scar_sample.r > 0.5) {
        base_color.rgb = mix(base_color.rgb, emission_composite, 0.85);
    }
    
    // Final output assignment with Ash Archive temporal retention
    COLOR = vec4(base_color.rgb + (emission_composite * 0.25), base_color.a);
}
