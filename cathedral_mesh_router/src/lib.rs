#![allow(non_snake_case)]
use wasm_bindgen::prelude::*;
use nalgebra::DMatrix;

#[wasm_bindgen]
pub struct WasmSpectralRouter {
    node_count: usize,
    adjacency: DMatrix<f64>,
}

#[wasm_bindgen]
impl WasmSpectralRouter {
    #[wasm_bindgen(constructor)]
    pub fn new(node_count: usize) -> WasmSpectralRouter {
        let adjacency = DMatrix::zeros(node_count, node_count);
        WasmSpectralRouter { node_count, adjacency }
    }

    pub fn add_edge(&mut self, u: usize, v: usize, weight: f64) {
        if u < self.node_count && v < self.node_count {
            self.adjacency[(u, v)] = weight;
            self.adjacency[(v, u)] = weight;
        }
    }

    pub fn remove_node(&mut self, node: usize) {
        if node < self.node_count {
            for i in 0..self.node_count {
                self.adjacency[(node, i)] = 0.0;
                self.adjacency[(i, node)] = 0.0;
            }
        }
    }

    pub fn build_laplacian(&self) -> DMatrix<f64> {
        let mut L = DMatrix::zeros(self.node_count, self.node_count);
        for i in 0..self.node_count {
            let mut degree = 0.0;
            for j in 0..self.node_count {
                let w = self.adjacency[(i, j)];
                if i != j && w > 0.0 {
                    degree += w;
                    L[(i, j)] = -w;
                }
            }
            L[(i, i)] = degree;
        }
        L
    }

    /// Computes the Fiedler eigenvalue (λ2 / μ2) via shifted power iteration
    pub fn compute_fiedler(&self) -> f64 {
        let L = self.build_laplacian();
        let mut lambda_max = 0.0;
        for i in 0..self.node_count {
            let mut row_sum = 0.0;
            for j in 0..self.node_count {
                row_sum += L[(i, j)].abs();
            }
            if row_sum > lambda_max {
                lambda_max = row_sum;
            }
        }

        if lambda_max == 0.0 {
            return 0.0;
        }

        let I = DMatrix::identity(self.node_count, self.node_count);
        let M = (lambda_max * I) - L;

        let mut v = nalgebra::DVector::from_element(self.node_count, 1.0);
        for _ in 0..120 {
            let v_next = &M * &v;
            let norm = v_next.norm();
            if norm == 0.0 { break; }
            v = v_next / norm;
        }

        let rayleigh = (v.transpose() * (&M * &v))[(0, 0)];
        let fiedler = lambda_max - rayleigh;
        if fiedler < 1e-6 { 0.0 } else { fiedler }
    }

    pub fn check_lex_vii(&self) -> bool {
        self.compute_fiedler() >= 0.05
    }
}
