use nalgebra::{DVector, DMatrix};

pub struct SpectralRouter {
    pub node_count: usize,
    pub adjacency: Vec<Vec<(usize, f32)>>,
    pub fiedler_vector: DVector<f32>,
    pub fiedler_value: f32,
}

impl SpectralRouter {
    pub fn new(node_count: usize) -> Self {
        Self {
            node_count,
            adjacency: vec![vec![]; node_count],
            fiedler_vector: DVector::from_element(node_count, 1.0 / (node_count as f32).sqrt()),
            fiedler_value: 0.0,
        }
    }

    fn build_laplacian(&self) -> DMatrix<f32> {
        let mut L = DMatrix::zeros(self.node_count, self.node_count);
        for i in 0..self.node_count {
            let mut degree = 0.0;
            for &(j, w) in &self.adjacency[i] {
                L[(i, j)] = -w;
                degree += w;
            }
            L[(i, i)] = degree;
        }
        L
    }

    pub fn compute_fiedler(&mut self, iterations: usize) {
        let L = self.build_laplacian();
        
        // FIX: Compute Rayleigh quotient BEFORE moving L
        let lv = &L * &self.fiedler_vector;
        self.fiedler_value = self.fiedler_vector.dot(&lv) / self.fiedler_vector.dot(&self.fiedler_vector);

        let lambda_max = L.row_iter().map(|row| row.abs().sum()).fold(0.0, f32::max);
        let I = DMatrix::identity(self.node_count, self.node_count);
        let M = (lambda_max * I) - L; // L is safely moved here now

        let mut v = DVector::from_element(self.node_count, 1.0);
        v.iter_mut().for_each(|x| *x = rand::random::<f32>());
        let trivial_eigenvector = DVector::from_element(self.node_count, 1.0 / (self.node_count as f32).sqrt());

        for _ in 0..iterations {
            let mut v_new = &M * &v;
            let dot_product = v_new.dot(&trivial_eigenvector);
            v_new -= trivial_eigenvector.clone() * dot_product;
            let norm = v_new.norm();
            if norm > 1e-6 { v_new /= norm; }
            v = v_new;
        }
        self.fiedler_vector = v;
    }

    pub fn check_partition_and_seppuku(&self, tx_power: &mut f32) -> bool {
        if self.fiedler_value < 0.01 {
            *tx_power = 0.0;
            return true;
        }
        false
    }
}
