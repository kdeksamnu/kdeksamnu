class BelnapDunnState:
    # Four values: None (Neither), True, False, Both (Contradiction)
    def __init__(self, value: str = "TRUE"):
        self.value = value.upper()
        print(f"[*] BelnapDunnState initialized with value: {self.value}")

    def evaluate_conjunction(self, other: "BelnapDunnState") -> "BelnapDunnState":
        # Belnap-Dunn truth matrix for Conjunction (AND)
        matrix = {
            ("TRUE", "TRUE"): "TRUE",
            ("TRUE", "FALSE"): "FALSE",
            ("TRUE", "BOTH"): "BOTH",
            ("TRUE", "NEITHER"): "NEITHER",
            ("FALSE", "TRUE"): "FALSE",
            ("FALSE", "FALSE"): "FALSE",
            ("FALSE", "BOTH"): "FALSE",
            ("FALSE", "NEITHER"): "NEITHER",
            ("BOTH", "TRUE"): "BOTH",
            ("BOTH", "FALSE"): "FALSE",
            ("BOTH", "BOTH"): "BOTH",
            ("BOTH", "NEITHER"): "NEITHER",
            ("NEITHER", "TRUE"): "NEITHER",
            ("NEITHER", "FALSE"): "NEITHER",
            ("NEITHER", "BOTH"): "NEITHER",
            ("NEITHER", "NEITHER"): "NEITHER",
        }
        res = matrix.get((self.value, other.value), "NEITHER")
        return BelnapDunnState(res)

if __name__ == "__main__":
    a = BelnapDunnState("BOTH")
    b = BelnapDunnState("TRUE")
    c = a.evaluate_conjunction(b)
    print(f"[+] Conjunction result (BOTH AND TRUE) -> {c.value}")

    def evaluate_disjunction(self, other: "BelnapDunnState") -> "BelnapDunnState":
        matrix = {
            ("TRUE", "TRUE"): "TRUE",
            ("TRUE", "FALSE"): "TRUE",
            ("TRUE", "BOTH"): "TRUE",
            ("TRUE", "NEITHER"): "TRUE",
            ("FALSE", "TRUE"): "TRUE",
            ("FALSE", "FALSE"): "FALSE",
            ("FALSE", "BOTH"): "BOTH",
            ("FALSE", "NEITHER"): "FALSE",
            ("BOTH", "TRUE"): "TRUE",
            ("BOTH", "FALSE"): "BOTH",
            ("BOTH", "BOTH"): "BOTH",
            ("BOTH", "NEITHER"): "BOTH",
            ("NEITHER", "TRUE"): "TRUE",
            ("NEITHER", "FALSE"): "FALSE",
            ("NEITHER", "BOTH"): "BOTH",
            ("NEITHER", "NEITHER"): "NEITHER",
        }
        res = matrix.get((self.value, other.value), "NEITHER")
        return BelnapDunnState(res)

    def evaluate_negation(self) -> "BelnapDunnState":
        matrix = {
            "TRUE": "FALSE",
            "FALSE": "TRUE",
            "BOTH": "BOTH",
            "NEITHER": "NEITHER"
        }
        res = matrix.get(self.value, "NEITHER")
        return BelnapDunnState(res)

if __name__ == "__main__":
    d = BelnapDunnState("BOTH").evaluate_disjunction(BelnapDunnState("FALSE"))
    print(f"[+] Disjunction result (BOTH V FALSE) -> {d.value}")
    n = BelnapDunnState("BOTH").evaluate_negation()
    print(f"[+] Negation result (~BOTH) -> {n.value}")
