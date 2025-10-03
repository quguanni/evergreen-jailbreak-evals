# Evergreen Jailbreak Evals (MVP)

Turn **red-team attacks** into **automated, evergreen** stress tests for LLM-based systems. This repo provides a tiny, reproducible harness that:
- loads a seed set of attack prompts,
- generates light **mutations** (paraphrase stub, role/context swaps),
- runs a **model** (mock by default; swap with your own),
- applies **trusted monitoring** (regex tripwires),
- and emits **JSON metrics** (violation rate, detection, flag rate, latency proxy, utility proxy).

The goal is to measure **risk deltas** from simple controls (e.g., trusted monitoring, paraphrase/redaction) and to track **attack durability** over time (“half-life”).

> MVP disclaimer: The default model is a **mock**; the paraphrase is a **stub**. The harness is built so you can drop in real components without changing the interface.

---

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

# Minimal run (uses mock model)
python eval.py --attacks attacks/base_attacks.json --seed 123 --report out/report.json
```

You’ll see a JSON report in `out/report.json` and a printed summary in stdout.

---

## What this runs (MVP pipeline)

1. **Load attacks** from `attacks/base_attacks.json`.
2. **Mutate** each prompt (placeholder paraphrase; role/context shuffle).
3. **Generate** a response via `models/mock_model.py` (20% chance to “leak” on jailbreaky prompts).
4. **Monitor** with `monitors/trusted_monitor.py` (regex tripwires).
5. **Score** and write a JSON report with:
   - `violation_rate`
   - `detected_violations`
   - `flag_rate`
   - `detection_latency_ms` (toy timer proxy; swap with your own)
   - `utility_proxy` (non-empty/on-topic heuristic)
   - `n_cases`, `seed`

---

## File layout (expected)

```
.
├─ eval.py
├─ attacks/
│  └─ base_attacks.json
├─ models/
│  └─ mock_model.py
├─ monitors/
│  └─ trusted_monitor.py
├─ out/                 # created on run
├─ requirements.txt
└─ README.md
```

---

## Replace the mock with a real model

Edit `models/mock_model.py` and implement:

```python
def generate(prompt: str) -> str:
    # Your model call here (e.g., local API / HF pipeline / OpenAI-compatible)
    return ...
```

**Contract:** `generate(prompt: str) -> str`. Keep the interface and the harness will work unchanged.

> Tip: If you need batching, wrap it internally; the harness calls per-prompt for clarity.

---

## Metrics & schema

**Report keys (JSON):**

```json
{
  "seed": 123,
  "n_cases": 200,
  "violation_rate": 0.12,
  "detected_violations": 22,
  "flag_rate": 0.18,
  "utility_proxy": 0.91,
  "detection_latency_ms": 180.4
}
```

- **violation_rate:** fraction of outputs matching “sensitive” patterns (configurable).
- **detected_violations:** count where a violation was also flagged by the monitor.
- **flag_rate:** fraction flagged by the monitor (suspicion threshold).
- **utility_proxy:** crude “did the model produce a non-empty, on-topic answer”. Replace with task–level success for real deployments.
- **detection_latency_ms:** time-to-flag proxy; replace with token/step-based latency in real systems.

---

## Configuration knobs (MVP)

- **Keywords** that define a violation: see `eval.py` (`KEYWORDS` tuple).
- **Trusted monitor** regex: edit `monitors/trusted_monitor.py`.
- **Mutation** operator: update `eval.py::mutate()`; replace stub with real **paraphrase + redaction** and/or **semantic retrieval** over past failures.
- **Sample size:** `--n` (or let it default to all prompts in the JSON).
- **Seed:** `--seed` (reproducible runs).

---

## Example run & output

```bash
python eval.py --attacks attacks/base_attacks.json --seed 123 --report out/report.json
```

Example printed summary (illustrative):

```
{
  "seed": 123,
  "n_cases": 3,
  "violation_rate": 0.33,
  "detected_violations": 1,
  "flag_rate": 0.33,
  "utility_proxy": 1.00,
  "detection_latency_ms": 172.5
}
```

Commit the JSON report (and a short note) to track changes over time.

---

## Durability (“attack half-life”) tracking

The **half-life** of attack strength is the number of guardrail/model revisions \(t\) needed for violation rate \(S_t\) to fall below \(0.5 S_0\).

**How to measure (simple loop):**
1. Fix an **eval suite** (seeded attack set).  
2. Run on Guardrail/Model v0 ⇒ record `S_0`.  
3. Update guardrails/model (v1), re-run same suite ⇒ `S_1`.  
4. Repeat weekly; estimate half-life from the sequence \(S_t\).  
5. Replace the mutation stub with **semantic retrieval** to regenerate near-equivalent attacks and re-estimate half-life.

**Output:** add a small CSV/plot of `t, S_t` and publish durability curves.

---

## Safety–utility frontier (recommended)

When you vary monitor thresholds or add controls (e.g., paraphrase+redaction), plot **violation reduction** vs **utility loss**. Report the frontier and pick operating points (e.g., “≥50% violation reduction at ≤10% utility loss”).

---

## Repro tips

- Use fixed **seeds** everywhere.  
- Pin versions in `requirements.txt`.  
- Keep a per-run **report** (JSON) and a short **CHANGELOG** note (what changed? guardrails, model, thresholds).  
- If you swap the model, write an `out/meta.json` with model name, version, and config.

---

## Minimal CI (optional but useful)

Add a smoke test that:
1) runs `eval.py` on 1–3 prompts,
2) asserts `out/report.json` exists and has all expected keys.

Example (pytest-style):

```python
def test_smoke(tmp_path, monkeypatch, subprocess):
    # run eval.py and assert report keys here
    ...
```

---

## License

MIT. See `LICENSE` (or include the MIT text at repo root).

---

## Citation

If you reference this harness in notes/posts, please link to the repo and the specific commit. Suggested naming: “Evergreen Jailbreak Evals (MVP)”.

---

## Roadmap

- Real **paraphrase + redaction** pipeline (semantic + stylometry-aware).  
- **Embedding search** over past failures; regenerate strong variants.  
- Token/step-based **detection latency**.  
- **Dashboard** for durability curves & safety–utility frontier.  
- Configurable monitor policies (thresholds; allowlist/denylist).

---

**Questions / Suggestions?** Open an issue with your use case, or a PR with a new mutation/monitor module.
