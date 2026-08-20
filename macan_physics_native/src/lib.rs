//! macan_physics_native
//!
//! Native Rust replacements for the hot per-frame loops in
//! `core/physics.py` and `game/particles.py`.
//!
//! Semantics are a 1:1 port of the original Python implementations so
//! either path (native or pure-Python fallback) produces identical
//! results. See the matching Python wrappers for the fallback logic.

use pyo3::prelude::*;

/// Player gravity + friction + Euler integration step.
///
/// Mirrors the first half of `PhysicsEngine.update()` in physics.py
/// (everything before `_resolve_tile_collisions` is called).
///
/// Returns (new_x, new_y, new_vx, new_vy).
#[pyfunction]
#[pyo3(signature = (
    x, y, vx, vy, on_ground, delta_time,
    gravity, max_fall_speed, ground_friction, air_resistance
))]
#[allow(clippy::too_many_arguments)]
fn physics_integrate(
    x: f64,
    y: f64,
    vx: f64,
    vy: f64,
    on_ground: bool,
    delta_time: f64,
    gravity: f64,
    max_fall_speed: f64,
    ground_friction: f64,
    air_resistance: f64,
) -> (f64, f64, f64, f64) {
    let mut vx = vx;
    let mut vy = vy;

    if !on_ground {
        vy += gravity * delta_time;
        if vy > max_fall_speed {
            vy = max_fall_speed;
        }
    }

    if !on_ground {
        vx *= air_resistance;
    } else {
        vx *= ground_friction;
    }

    let new_x = x + vx * delta_time;
    let new_y = y + vy * delta_time;

    (new_x, new_y, vx, vy)
}

/// Resolve AABB collisions between the player and a list of solid tile
/// rects, in the same order the tiles were visited in Python
/// (`_resolve_tile_collisions` / `_resolve_aabb_collision`).
///
/// `tiles` is a list of (tx1, ty1, tx2, ty2) rects — already filtered
/// to solid, non-empty tiles by the Python side (tilemap lookups stay
/// in Python since the tilemap object lives there).
///
/// Returns (new_x, new_y, new_vx, new_vy, on_ground, jumps_remaining).
#[pyfunction]
#[pyo3(signature = (x, y, vx, vy, width, height, jumps_remaining, max_jumps, tiles))]
#[allow(clippy::too_many_arguments)]
fn physics_resolve_collisions(
    x: f64,
    y: f64,
    vx: f64,
    vy: f64,
    width: f64,
    height: f64,
    jumps_remaining: i32,
    max_jumps: i32,
    tiles: Vec<(f64, f64, f64, f64)>,
) -> (f64, f64, f64, f64, bool, i32) {
    let mut px = x;
    let mut py = y;
    let mut pvx = vx;
    let mut pvy = vy;
    let mut on_ground = false;
    let mut jumps = jumps_remaining;

    for (tx1, ty1, tx2, ty2) in tiles {
        let px1 = px;
        let py1 = py;
        let px2 = px + width;
        let py2 = py + height;

        // AABB intersect check
        if !(px1 < tx2 && px2 > tx1 && py1 < ty2 && py2 > ty1) {
            continue;
        }

        let overlap_left = px2 - tx1;
        let overlap_right = tx2 - px1;
        let overlap_top = py2 - ty1;
        let overlap_bottom = ty2 - py1;

        let min_overlap = overlap_left
            .min(overlap_right)
            .min(overlap_top)
            .min(overlap_bottom);

        if min_overlap == overlap_top && pvy > 0.0 {
            // Falling onto a tile from above
            py = ty1 - height;
            pvy = 0.0;
            on_ground = true;
            jumps = max_jumps;
        } else if min_overlap == overlap_bottom && pvy < 0.0 {
            // Hit a ceiling
            py = ty2;
            pvy = 0.0;
        } else if min_overlap == overlap_left && pvx > 0.0 {
            px = tx1 - width;
            pvx = 0.0;
        } else if min_overlap == overlap_right && pvx < 0.0 {
            px = tx2;
            pvx = 0.0;
        }
    }

    (px, py, pvx, pvy, on_ground, jumps)
}

/// Batch-update every particle's physics in one native call instead of
/// one Python-level `Particle.update()` call per particle per frame.
///
/// Input tuple per particle: (x, y, vx, vy, age, lifetime, initial_size)
/// Output tuple per particle: (x, y, vx, vy, size, age, alive)
///
/// Order of the output list matches the order of the input list, so the
/// Python side can zip() the results straight back onto its Particle
/// objects.
#[pyfunction]
#[pyo3(signature = (particles, delta_time, gravity=300.0))]
fn particles_update_batch(
    particles: Vec<(f64, f64, f64, f64, f64, f64, f64)>,
    delta_time: f64,
    gravity: f64,
) -> Vec<(f64, f64, f64, f64, f64, f64, bool)> {
    let mut out = Vec::with_capacity(particles.len());

    for (x, y, vx, vy, age, lifetime, initial_size) in particles {
        let new_age = age + delta_time;

        if new_age >= lifetime {
            // Expired - Python will drop this particle. Position/velocity
            // values are irrelevant once alive=false, but returned as-is.
            out.push((x, y, vx, vy, initial_size, new_age, false));
            continue;
        }

        let new_vy = vy + gravity * delta_time;
        let new_x = x + vx * delta_time;
        let new_y = y + new_vy * delta_time;

        let life_ratio = new_age / lifetime;
        let new_size = initial_size * (1.0 - life_ratio * 0.5);

        out.push((new_x, new_y, vx, new_vy, new_size, new_age, true));
    }

    out
}

#[pymodule]
fn macan_physics_native(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(physics_integrate, m)?)?;
    m.add_function(wrap_pyfunction!(physics_resolve_collisions, m)?)?;
    m.add_function(wrap_pyfunction!(particles_update_batch, m)?)?;
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    Ok(())
}
