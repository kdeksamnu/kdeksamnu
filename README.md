# MLAOS-PRIME // System Architecture & Engine

> *The mythotechnical engine and architectural codex of MLAOS-PRIME.*

## The Vision
MLAOS-PRIME is a large-scale systems architecture project combining engineering, computer science, and speculative worldbuilding. This repository houses both the philosophical **Codex** and the executable **Engine**. 

Commercial implementations, microservices, and automation pipelines derived from this architecture are deployed via **Dallmier Tech Venture**.

## The Architecture
The system enforces a strict separation of concerns:
* **\`/codex\`**: The philosophical and architectural specifications.
* **\`/engine\`**: The FastAPI execution layer. Transport logic is strictly decoupled from domain logic.
* **\`/rituals\`**: Automated pipelines, CLI utilities, and data transformations.

## The Aesthetic of Code
We do not merely write code; we engineer resilient systems.
1. **Strict Decoupling**: Route handlers are traffic controllers. Domain logic resides in services.
2. **Boundary Sanitization**: Pydantic validates at the gate. Invalid inputs are rejected with precise \`422\` diagnostics.
3. **Defensive Persistence**: All SQL operations utilize explicit parameterized binding.
4. **Symmetric Testing**: We test the shadows. Failure states are verified with the same rigor as happy paths.
5. **Observability**: Standardized latency headers (\`X-Process-Time-Ms\`) and health probes are native.

## Quickstart

\`\`\`bash
# Install dependencies
make install

# Ignite the engine
make dev

# Run the proving grounds (tests)
make test
\`\`\`
