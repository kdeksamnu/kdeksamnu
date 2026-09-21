#version 450
layout(local_size_x = 8, local_size_y = 8, local_size_z = 1) in;

layout(push_constant) uniform PushConstants {
    uint grid_width;
    uint grid_height;
} constants;

// Voxel payload: [TruthVal, sigma_x, sigma_y, tau_xy]
// TruthVal: 0 = N, 1 = F, 2 = T, 3 = B
layout(set = 0, binding = 0, std430) readonly buffer VoxelStateBuffer {
    vec4 cells[];
};

// Target output: [isMagicAligned, cos2Theta, residualShear, needsSqueeze]
layout(set = 0, binding = 1, std430) writeonly buffer OutputBuffer {
    vec4 results[];
};

const float MAGIC_ANGLE_COS2 = -0.33333333;
const float SHEAR_TOLERANCE  = 0.015;

void main() {
    uint width = (constants.grid_width > 0) ? constants.grid_width : 64;
    uint index = gl_GlobalInvocationID.y * width + gl_GlobalInvocationID.x;
    vec4 cell  = cells[index];

    int truthVal   = int(cell.x);
    float sigma_x  = cell.y;
    float sigma_y  = cell.z;
    float tau_xy   = cell.w;

    // 1. Compute cos(2 * theta_p) via Mohr's circle without transcendental functions
    float deltaSigma = sigma_x - sigma_y;
    float denom = sqrt(deltaSigma * deltaSigma + 4.0 * tau_xy * tau_xy);
    
    // Guard against division by zero in hydrostatic/uniform stress states
    float cos2Theta = (denom > 1e-6) ? (deltaSigma / denom) : 0.0;

    // 2. Evaluate Magic-Angle Alignment (|cos(2*theta) - (-1/3)| <= tolerance)
    float alignmentError = abs(cos2Theta - MAGIC_ANGLE_COS2);
    float isMagicAligned = (alignmentError <= SHEAR_TOLERANCE) ? 1.0 : 0.0;

    // 3. Zero out shear when magic-aligned; retain active shear otherwise
    float residualShear = tau_xy * (1.0 - isMagicAligned);

    // 4. Trigger Metamorphic Squeeze: State B (3) + critical shear + magic alignment
    float needsSqueeze = (truthVal == 3 && abs(tau_xy) > 0.1 && isMagicAligned > 0.5) ? 1.0 : 0.0;

    results[index] = vec4(isMagicAligned, cos2Theta, residualShear, needsSqueeze);
}
