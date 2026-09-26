class DialetheicHeatSink:
    def __init__(self, dissipation_rate: float = 1.5):
        self.dissipation_rate = dissipation_rate
        print(f"[*] DialetheicHeatSink initialized with rate: {dissipation_rate} Hz")

    def absorb_contradiction(self, scar_count: int) -> float:
        thermal_load = scar_count * self.dissipation_rate
        print(f"[+] Absorbed {scar_count} harmonic scars. Current thermal load: {thermal_load}")
        return thermal_load

if __name__ == "__main__":
    sink = DialetheicHeatSink()
    sink.absorb_contradiction(4)
