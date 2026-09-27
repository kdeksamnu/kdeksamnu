class BelnapDunnState:
    def __init__(self, value: str):
        if value not in ["T", "F", "B", "N"]:
            raise ValueError(f"Invalid Belnap-Dunn value: {value}. Must be T, F, B, or N.")
        self.value = value

    def evaluate_conjunction(self, other: "BelnapDunnState") -> "BelnapDunnState":
        # Meet under truth ordering (t-order)
        matrix = {
            ("T", "T"): "T", ("T", "F"): "F", ("T", "B"): "B", ("T", "N"): "N",
            ("F", "T"): "F", ("F", "F"): "F", ("F", "B"): "F", ("F", "N"): "F",
            ("B", "T"): "B", ("B", "F"): "F", ("B", "B"): "B", ("B", "N"): "N",
            ("N", "T"): "N", ("N", "F"): "F", ("N", "B"): "N", ("N", "N"): "N"
        }
        res = matrix.get((self.value, other.value), "N")
        return BelnapDunnState(res)

    def evaluate_disjunction(self, other: "BelnapDunnState") -> "BelnapDunnState":
        # Join under truth ordering (t-order)
        matrix = {
            ("T", "T"): "T", ("T", "F"): "T", ("T", "B"): "T", ("T", "N"): "T",
            ("F", "T"): "T", ("F", "F"): "F", ("F", "B"): "B", ("F", "N"): "N",
            ("B", "T"): "T", ("B", "F"): "B", ("B", "B"): "B", ("B", "N"): "T",
            ("N", "T"): "T", ("N", "F"): "N", ("N", "B"): "T", ("N", "N"): "N"
        }
        res = matrix.get((self.value, other.value), "N")
        return BelnapDunnState(res)

    def evaluate_negation(self) -> "BelnapDunnState":
        matrix = {
            "T": "F",
            "F": "T",
            "B": "B",
            "N": "N"
        }
        res = matrix.get(self.value, "N")
        return BelnapDunnState(res)

if __name__ == "__main__":
    t = BelnapDunnState("T")
    f = BelnapDunnState("F")
    b = BelnapDunnState("B")
    n = BelnapDunnState("N")
    
    conj = t.evaluate_conjunction(b)
    disj = f.evaluate_disjunction(b)
    neg = b.evaluate_negation()
    
    print(f"[+] Belnap-Dunn Phase 02 Logic Layer Initialized.")
    print(f"[+] Conjunction (T AND B) -> {conj.value}")
    print(f"[+] Disjunction (F OR B) -> {disj.value}")
    print(f"[+] Negation (~B) -> {neg.value}")
