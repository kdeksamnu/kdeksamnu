shader_type spatial;
render_mode blend_mix, depth_draw_opaque, cull_back, diffuse_burley, specular_schlick_ggx;

uniform vec3 u_color_lumen = vec3(0.98, 0.85, 0.35); // Radiant Kintsugi Gold
uniform vec3 u_color_shadow = vec3(0.04, 0.04, 0.06); // Obsidian Null
uniform float u_quadrature_squeeze : hint_range(0.0, 1.0) = 0.68;
uniform float u_dither_strength : hint_range(0.0, 1.0) = 0.45;

varying vec3 v_world_pos;
varying vec3 v_normal;

float get_bayer_4x4(vec2 screen_pos) {
    int x = int(screen_pos.x) % 4;
    int y = int(screen_pos.y) % 4;
    int index = x + y * 4;
    
    int bayer[16] = int[](
        0,  8,  2, 10,
        12, 4, 14,  6,
        3, 11,  1,  9,
        15, 7, 13,  5
    );
    return float(bayer[index]) / 16.0;
}

void vertex() {
    v_world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
    v_normal = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

void fragment() {
    vec3 view_dir = normalize(CAMERA_POSITION_WORLD - v_world_pos);
    float n_dot_v = max(dot(v_normal, view_dir), 0.0);
    
    float threshold = 0.5 + (u_quadrature_squeeze - 0.5) * 0.3;
    float dither = get_bayer_4x4(FRAGCOORD.xy);
    float stepped_lum = step(threshold + (dither - 0.5) * u_dither_strength, n_dot_v);
    
    vec3 albedo = mix(u_color_shadow, u_color_lumen, stepped_lum);
    vec3 emission = u_color_lumen * (1.0 - stepped_lum) * (1.0 - u_quadrature_squeeze) * 0.4;
    
    ALBEDO = albedo;
    EMISSION = emission;
    ROUGHNESS = 0.35 + (1.0 - stepped_lum) * 0.4;
    METALLIC = stepped_lum * 0.85;
}
