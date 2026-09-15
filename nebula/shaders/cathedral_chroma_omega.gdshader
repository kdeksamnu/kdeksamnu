shader_type spatial;
render_mode blend_mix, depth_draw_opaque, cull_back, diffuse_burley, specular_schlick_ggx;

const vec3 COLOR_THETA_GOLD    = vec3(0.85, 0.68, 0.22);
const vec3 COLOR_DELTA_BLUE    = vec3(0.08, 0.18, 0.36);
const vec3 COLOR_PSI_TEAL      = vec3(0.12, 0.52, 0.54);
const vec3 COLOR_NULL_OBSIDIAN = vec3(0.04, 0.04, 0.06);
const vec3 COLOR_KINTSUGI_HOT  = vec3(1.00, 0.82, 0.30);
const vec3 COLOR_LANDAUER_IR   = vec3(1.00, 0.35, 0.05);

uniform int u_monad_id : hint_range(1, 12) = 1;
uniform float u_opacity : hint_range(0.0, 1.0) = 0.85;
uniform float u_audit_intensity : hint_range(0.0, 5.0) = 0.0;
uniform float u_scar_cost : hint_range(0.0, 0.30) = 0.14;

varying vec3 v_world_pos;
varying vec3 v_normal;

void vertex() {
    v_world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
    v_normal = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

void fragment() {
    vec3 view_dir = normalize(CAMERA_POSITION_WORLD - v_world_pos);
    float n_dot_v = max(dot(v_normal, view_dir), 0.0);

    vec3 base_albedo = COLOR_NULL_OBSIDIAN;
    vec3 emission_color = vec3(0.0);
    float roughness = 0.45;
    float metallic = 0.10;

    if (u_monad_id == 1) {
        base_albedo = mix(COLOR_NULL_OBSIDIAN, COLOR_THETA_GOLD, n_dot_v * 0.8 + 0.2);
        metallic = 0.85;
        roughness = 0.20;
    } else if (u_monad_id == 2) {
        base_albedo = COLOR_NULL_OBSIDIAN;
        roughness = 0.90;
    } else if (u_monad_id == 8 || u_monad_id == 9) {
        base_albedo = mix(COLOR_DELTA_BLUE, vec3(0.35, 0.15, 0.55), sin(v_world_pos.y * 2.0) * 0.5 + 0.5);
        roughness = 0.30;
    } else if (u_monad_id == 11) {
        vec2 local_coord = UV - vec2(0.5);
        float theta = atan(local_coord.y, local_coord.x);
        float r = length(local_coord);
        float branch_cut = sqrt(max(r, 0.001)) * cos(theta * 0.5);
        base_albedo = mix(COLOR_NULL_OBSIDIAN, COLOR_KINTSUGI_HOT, step(0.0, branch_cut));
        emission_color = COLOR_KINTSUGI_HOT * abs(branch_cut) * (u_scar_cost / 0.30) * 3.0;
        metallic = 0.95;
        roughness = 0.15;
    } else {
        base_albedo = vec3(0.15, 0.18, 0.22);
        roughness = 0.60;
    }

    if (u_opacity < 0.40 && u_audit_intensity > 0.01) {
        float pulse = sin(TIME * 6.28318 * 1.5) * 0.5 + 0.5;
        emission_color += COLOR_LANDAUER_IR * u_audit_intensity * (1.0 - u_opacity) * (pulse * 0.7 + 0.3);
    }

    ALBEDO = base_albedo;
    METALLIC = metallic;
    ROUGHNESS = roughness;
    EMISSION = emission_color;
    ALPHA = clamp(u_opacity + (u_audit_intensity * 0.15), 0.05, 1.0);
}
