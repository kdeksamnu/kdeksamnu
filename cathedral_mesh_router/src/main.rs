mod spectral;
use spectral::SpectralRouter;

fn main() {
    println!("==================================================================");
    println!(" CATHEDRAL ENGINE: DIMENSION 8 - SPECTRAL MESH ROUTER");
    println!("==================================================================");
    let mut router = SpectralRouter::new(4);
    router.adjacency[0] = vec![(1, 1.0), (2, 1.0)];
    router.adjacency[1] = vec![(0, 1.0), (2, 1.0)];
    router.adjacency[2] = vec![(0, 1.0), (1, 1.0)];
    // Node 3 is isolated (Ghost)
    router.compute_fiedler(50);
    println!("[TOPOLOGY] Fiedler Value (λ₂): {:.6}", router.fiedler_value);
    let mut tx = 1.0;
    if router.check_partition_and_seppuku(&mut tx) {
        println!("[LEX VII] SEPPUKU EXECUTED. Node isolated.");
    } else {
        println!("[LEX VII] Node active. Mesh healthy.");
    }
}
