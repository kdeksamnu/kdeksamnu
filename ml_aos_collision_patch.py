# MLAOS-Prime // Sliding-Vector Collision Resolution Pass
# Replaces strict stopping with tangent sliding vectors against cathedral pillar boundaries.

def resolve_isometric_collision(player_pos, intended_delta, collision_grid):
    """
    Evaluates proposed movement against the high-density isometric wall mask.
    If a direct collision occurs, decomposes the movement vector into tangential sliding components.
    """
    x, y = player_pos
    dx, dy = intended_delta
    target_x = x + dx
    target_y = y + dy

    # Check primary target node
    if not collision_grid.is_solid(target_x, target_y):
        return (target_x, target_y), "NOMINAL_MOVE"

    # Slide Vector Resolution: Try X-axis movement independently
    if not collision_grid.is_solid(target_x, y):
        return (target_x, y), "SLIDE_X_AXIS"

    # Slide Vector Resolution: Try Y-axis movement independently
    if not collision_grid.is_solid(x, target_y):
        return (x, target_y), "SLIDE_Y_AXIS"

    # Full obstruction: maintain current position and log Ash Archive warning
    return (x, y), "OBSTRUCTION_LOCKED"

if __name__ == "__main__":
    print("[COLLISION PATCH] `ml_aos_collision_patch.py` loaded successfully into the runtime environment.")
