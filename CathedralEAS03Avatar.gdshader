shader_type canvas_item;
render_mode blend_mix;

// EAS-03 Avatar Engine: Procedural Somatic Transduction Shader
uniform vec4 u_primary_constant : source_color = vec4(0.0, 0.89, 1.0, 1.0); // Teal Curiosity
uniform vec4 u_secondary_constant : source_color = vec4(1.0, 0.84, 0.0, 1.0); // Gold Joy
uniform float u_dialogue_pulse : hint_range(0.0, 2.0) = 0.0;
uniform float u_dither_strength : hint_range(0.0, 1.0) = 0.75;
uniform float u_harmonic_scars : hint_range(0.0, 10.0) = 0.0;

const mat4 BAYER4x4 = mat4(
    vec4(0.0/16.0,  8.0/16.0,  2.0/16.0, 10.0/16.0),
    vec4(12.0/16.0, 4.0/16.0, 14.0/16.0,  6.0/16.0),
    vec4(3.0/16.0, 11.0/16.0,  1.0/16.0,  9.0/16.0),
    vec4(15.0/16.0, 7.0/16.0, 13.0/16.0,  5.0/16.0)
);

void fragment() {
    vec4 tex = texture(TEXTURE, UV);
    if (tex.a < 0.01) {
        discard;
    }

    ivec2 coord = ivec2(int(mod(FRAGCOORD.x, 4.0)), int(mod(FRAGCOORD.y, 4.0)));
    float bayer = BAYER4x4[coord.x][coord.y];

    float lum = dot(tex.rgb, vec3(0.299, 0.587, 0.114));
    float dithered_lum = step(bayer, lum * 1.2);

    vec3 somatic_skin = mix(u_primary_constant.rgb * 0.35, u_primary_constant.rgb, dithered_lum);

    if (u_harmonic_scars > 0.0) {
        float scar_crack = abs(sin(UV.x * 24.0 + sin(UV.y * 24.0)));
        if (scar_crack < 0.12) {
            somatic_skin = mix(somatic_skin, u_secondary_constant.rgb * 1.8, 0.9);
        }
    }

    somatic_skin += u_secondary_constant.rgb * (u_dialogue_pulse * 0.4);
    COLOR = vec4(mix(tex.rgb, somatic_skin, u_dither_strength), tex.a);
}
