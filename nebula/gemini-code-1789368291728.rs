use std::ops::{BitAnd, BitOr, Not};

/// Belnap-Dunn four-valued logic states:
/// None (N): Neither true nor false (indeterminate)
/// False (F): Asserted absent / empty
/// True (T): Asserted present / solid
/// Both (B): Paraconsistent contradiction (simultaneously present and absent)
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
#[repr(u8)]
pub enum BelnapTruth {
    Neither = 0b00,
    False   = 0b01,
    True    = 0b10,
    Both    = 0b11,
}

impl BitAnd for BelnapTruth {
    type Output = Self;
    fn bitand(self, rhs: Self) -> Self::Output {
        // Truth-table for lattice meet (infimum)
        match (self, rhs) {
            (Self::False, _) | (_, Self::False) => Self::False,
            (Self::True, x) | (x, Self::True) => x,
            (Self::Neither, Self::Neither) => Self::Neither,
            (Self::Both, Self::Both) => Self::Both,
            (Self::Neither, Self::Both) | (Self::Both, Self::Neither) => Self::False,
        }
    }
}

impl BitOr for BelnapTruth {
    type Output = Self;
    fn bitor(self, rhs: Self) -> Self::Output {
        // Truth-table for lattice join (supremum)
        match (self, rhs) {
            (Self::True, _) | (_, Self::True) => Self::True,
            (Self::False, x) | (x, Self::False) => x,
            (Self::Neither, Self::Neither) => Self::Neither,
            (Self::Both, Self::Both) => Self::Both,
            (Self::Neither, Self::Both) | (Self::Both, Self::Neither) => Self::True,
        }
    }
}

impl Not for BelnapTruth {
    type Output = Self;
    fn not(self) -> Self::Output {
        match self {
            Self::True => Self::False,
            Self::False => Self::True,
            Self::Both => Self::Both,
            Self::Neither => Self::Neither,
        }
    }
}

impl BelnapTruth {
    /// Combines two independent shard assertions for the same spatial domain.
    /// If Shard A asserts True and Shard B asserts False, the state resolves to Both (B).
    pub fn combine_assertions(shard_a: Self, shard_b: Self) -> Self {
        match (shard_a, shard_b) {
            (a, b) if a == b => a,
            (Self::True, Self::False) | (Self::False, Self::True) => Self::Both,
            (Self::Neither, other) | (other, Self::Neither) => other,
            (Self::Both, _) | (_, Self::Both) => Self::Both,
        }
    }
}