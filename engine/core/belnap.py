from enum import Enum

class TruthValue(Enum):
    TRUE = "T"
    FALSE = "F"
    BOTH = "B"
    NEITHER = "N"

class BelnapMatrix:
    @staticmethod
    def conjunction(a: TruthValue, b: TruthValue) -> TruthValue:
        table = {
            (TruthValue.TRUE, TruthValue.TRUE): TruthValue.TRUE,
            (TruthValue.TRUE, TruthValue.FALSE): TruthValue.FALSE,
            (TruthValue.TRUE, TruthValue.BOTH): TruthValue.BOTH,
            (TruthValue.TRUE, TruthValue.NEITHER): TruthValue.NEITHER,
            (TruthValue.FALSE, TruthValue.FALSE): TruthValue.FALSE,
            (TruthValue.FALSE, TruthValue.BOTH): TruthValue.FALSE,
            (TruthValue.FALSE, TruthValue.NEITHER): TruthValue.FALSE,
            (TruthValue.BOTH, TruthValue.BOTH): TruthValue.BOTH,
            (TruthValue.BOTH, TruthValue.NEITHER): TruthValue.NEITHER,
            (TruthValue.NEITHER, TruthValue.NEITHER): TruthValue.NEITHER,
        }
        return table.get((a, b)) or table.get((b, a), TruthValue.NEITHER)

    @staticmethod
    def disjunction(a: TruthValue, b: TruthValue) -> TruthValue:
        table = {
            (TruthValue.TRUE, TruthValue.TRUE): TruthValue.TRUE,
            (TruthValue.TRUE, TruthValue.FALSE): TruthValue.TRUE,
            (TruthValue.TRUE, TruthValue.BOTH): TruthValue.TRUE,
            (TruthValue.TRUE, TruthValue.NEITHER): TruthValue.TRUE,
            (TruthValue.FALSE, TruthValue.FALSE): TruthValue.FALSE,
            (TruthValue.FALSE, TruthValue.BOTH): TruthValue.BOTH,
            (TruthValue.FALSE, TruthValue.NEITHER): TruthValue.FALSE,
            (TruthValue.BOTH, TruthValue.BOTH): TruthValue.BOTH,
            (TruthValue.BOTH, TruthValue.NEITHER): TruthValue.BOTH,
            (TruthValue.NEITHER, TruthValue.NEITHER): TruthValue.NEITHER,
        }
        return table.get((a, b)) or table.get((b, a), TruthValue.NEITHER)
