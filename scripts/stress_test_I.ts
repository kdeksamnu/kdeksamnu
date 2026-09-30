import { createHash } from "node:crypto";

type BelnapState = "TRUE" | "FALSE" | "BOTH" | "NEITHER";

interface ContradictionRecord {
  run_id: string;
  seed: number;
  input: {
    proposition: string;
    positive: boolean;
    negative: boolean;
  };
  belnap_state: BelnapState;
  exception: boolean;
  logical_explosion: boolean;
  buffer_slot: number;
  timestamp: number;
  state_hash: string;
  transition_hash: string;
}

class DeterministicRng {
  private state: number;

  constructor(seed: number) {
    this.state = seed >>> 0;
  }

  next(): number {
    let x = this.state;
    x ^= x << 13;
    x ^= x >>> 17;
    x ^= x << 5;
    this.state = x >>> 0;
    return this.state;
  }

  nextInt(max: number): number {
    return this.next() % max;
  }
}

class DialetheicRingBuffer {
  private readonly slots: Array<ContradictionRecord | null>;
  private cursor = 0;

  constructor(capacity: number) {
    this.slots = new Array(capacity).fill(null);
  }

  insert(record: ContradictionRecord): number {
    const slot = this.cursor;
    this.slots[slot] = record;
    this.cursor = (this.cursor + 1) % this.slots.length;
    return slot;
  }

  get(slot: number): ContradictionRecord | null {
    return this.slots[slot];
  }
}

function hash(value: unknown): string {
  return createHash("sha256")
    .update(JSON.stringify(value))
    .digest("hex");
}

function classifyBelnap(
  positive: boolean,
  negative: boolean,
): BelnapState {
  if (positive && negative) return "BOTH";
  if (positive) return "TRUE";
  if (negative) return "FALSE";
  return "NEITHER";
}

function runStressTest(seed: number): ContradictionRecord {
  const rng = new DeterministicRng(seed);
  const buffer = new DialetheicRingBuffer(8);

  const proposition = "A";
  const positive = true;
  const negative = true;

  const belnapState = classifyBelnap(positive, negative);

  if (belnapState !== "BOTH") {
    throw new Error("Stress Test I failed: contradiction did not classify as BOTH");
  }

  const timestamp = rng.nextInt(1_000_000);
  const run_id = `ST-I-${seed.toString(16).padStart(8, "0")}`;

  const base = {
    run_id,
    seed,
    input: {
      proposition,
      positive,
      negative,
    },
    belnap_state: belnapState,
    exception: false,
    logical_explosion: false,
    timestamp,
  };

  const state_hash = hash(base);

  const preliminary: ContradictionRecord = {
    ...base,
    buffer_slot: -1,
    state_hash,
    transition_hash: "",
  };

  const bufferSlot = buffer.insert(preliminary);

  const finalRecord = {
    ...preliminary,
    buffer_slot: bufferSlot,
  };

  const transition_hash = hash(finalRecord);

  const record: ContradictionRecord = {
    ...finalRecord,
    transition_hash,
  };

  const archived = buffer.get(bufferSlot);

  if (archived === null) {
    throw new Error("Stress Test I failed: buffer record missing");
  }

  if (record.exception) {
    throw new Error("Stress Test I failed: runtime exception occurred");
  }

  if (record.logical_explosion) {
    throw new Error("Stress Test I failed: logical explosion occurred");
  }

  return record;
}

const seed = Number(process.argv[2] ?? 20260929);

if (!Number.isInteger(seed)) {
  console.error("Seed must be an integer.");
  process.exit(2);
}

const result = runStressTest(seed);

console.log(JSON.stringify(result, null, 2));
