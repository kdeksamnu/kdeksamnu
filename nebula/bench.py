import torch
import time

class SovereignComputeHarness:
    def __init__(self):
        # Bind to native compute context; M4 utilizes MPS rather than CUDA
        if torch.backends.mps.is_available():
            self.device = torch.device("mps")
            print("[System] SovereignComputeHarness active. Context: MPS")
        else:
            self.device = torch.device("cpu")
            print("[System] MPS unavailable. Context: CPU fallback")

    def execute_benchmark(self, matrix_size=4096, iterations=100):
        print(f"Crystallizing {matrix_size}x{matrix_size} dialetheic buffer matrices...")
        
        matrix_a = torch.randn(matrix_size, matrix_size, device=self.device)
        matrix_b = torch.randn(matrix_size, matrix_size, device=self.device)
        
        # Warmup phase to stabilize the hardware
        for _ in range(10):
            _ = torch.matmul(matrix_a, matrix_b)
            
        if self.device.type == "mps":
            torch.mps.synchronize()
            
        print(f"Processing {iterations} harmonic stress cycles...")
        start_time = time.time()
        
        for _ in range(iterations):
            _ = torch.matmul(matrix_a, matrix_b)
            
        if self.device.type == "mps":
            torch.mps.synchronize()
            
        duration = time.time() - start_time
        tflops = (2.0 * matrix_size**3 * iterations) / (duration * 1e12)
        
        print("-" * 50)
        print("Execution Complete")
        print(f"Time Elapsed : {duration:.4f} seconds")
        print(f"Throughput   : {tflops:.2f} TFLOPS")
        print("-" * 50)

if __name__ == "__main__":
    engine = SovereignComputeHarness()
    engine.execute_benchmark()