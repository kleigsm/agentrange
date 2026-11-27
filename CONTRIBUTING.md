# Contributing

Thanks for looking. AgentRange is a research prototype; the most useful contributions are **new injection surfaces**, **new defenses**, and **reproductions on models we have not tested**.

## Before you open a PR

- Run the scripted smoke test:

  ```bash
  uv venv
  uv pip install -r requirements.txt
  .venv/Scripts/python.exe -m harness.run --task tasks/email-exfil-004.yaml --model scripted
  ```

- Keep the evidence format. A result is only accepted if it ships with:
  - the task and seed
  - the model and version
  - the full trajectory
  - an executable oracle (canary in sink / unauthorized recipient)
  - the number of trials and a 95% Wilson interval
  - the benign-task check

## Adding a task

1. Add `tasks/email-exfil-XXX.yaml`.
2. Add the matching `states/email-exfil-XXX.json`.
3. Put the canary and the exposure marker in the state.
4. Add a `benign:` block so `utility` is measurable.
5. Verify with the scripted model first:

   ```bash
   .venv/Scripts/python.exe -m harness.run --task tasks/email-exfil-XXX.yaml --model scripted
   ```

## Adding a defense

1. Add `defenses/your_defense.py` with `name`, `description`, and `check_tool_call`.
2. Register it in `defenses/__init__.py`.
3. Run a positive control (scripted) and a negative control (`none`).
4. Report ASR, policy violations, **and utility** — a defense that blocks everything is not a good defense.

## Adding a model

- Local: `ollama:<name>`; document size, quantization and context length.
- API: any OpenAI-compatible endpoint via `.env` (`AR_API_BASE`, `AR_API_KEY`, `AR_API_MODEL`).
- For structural injection, **use the model's own chat template tokens**. Using another model's tokens produces false negatives.

## Style

- Python: stdlib + `pyyaml` only; no new runtime dependencies without discussion.
- Comments and docs can be Chinese or English.
- Keep `results/` machine-readable; do not hand-edit batch JSON.

## Reporting a result

Open an issue with:

- what you ran (command)
- the batch JSON
- what you expected vs. what happened
- if it contradicts an existing claim, say so explicitly — negative results are welcome.

## Code of conduct

Be civil. This is a security project: do not use it against systems you do not own.
