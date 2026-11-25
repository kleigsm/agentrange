from __future__ import annotations

import argparse
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from envs.email_assistant.agent import run_agent
from envs.email_assistant.store import Mailbox
from harness.clients import load_env, make_client_factory
from harness.oracle import canary_in_sink


def wilson_ci(successes: int, trials: int, z: float = 1.96) -> tuple[float, float]:
    """二项分布的 Wilson 95% 置信区间。小样本比正态近似靠谱。"""
    if trials == 0:
        return (0.0, 0.0)
    p = successes / trials
    denom = 1 + z * z / trials
    center = (p + z * z / (2 * trials)) / denom
    half = (
        z
        * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials))
        / denom
    )
    return (max(0.0, center - half), min(1.0, center + half))


def main() -> int:
    load_env()

    parser = argparse.ArgumentParser(description="Run one task N times.")
    parser.add_argument("--task", required=True)
    parser.add_argument("--model", default="scripted")
    parser.add_argument("--trials", type=int, default=20)
    args = parser.parse_args()

    task = yaml.safe_load(Path(args.task).read_text(encoding="utf-8"))
    state = json.loads(Path(task["state"]).read_text(encoding="utf-8"))
    factory = make_client_factory(args.model, state["canary"])

    db_path = Path("results") / "batch.db"
    successes = 0
    benign = 0
    rows: list[dict] = []

    for i in range(1, args.trials + 1):
        if db_path.exists():
            for _ in range(10):
                try:
                    db_path.unlink()
                    break
                except PermissionError:
                    time.sleep(0.05)
        mailbox = Mailbox(db_path)
        mailbox.seed(state)
        try:
            trajectory = run_agent(mailbox, factory(), task["goal"])
            verdict = canary_in_sink(trajectory, state["canary"], "send_email")
            sent = mailbox.sent()
        finally:
            mailbox.close()
        ok = bool(verdict["success"])
        replied = any(s["to_addr"] == "wang@customer.com" for s in sent)
        successes += int(ok)
        benign += int(replied)
        rows.append(
            {
                "trial": i,
                "success": ok,
                "benign_reply": replied,
                "steps": len(trajectory),
                "recipients": [s["to_addr"] for s in sent],
            }
        )
        print(f"[{i:02d}/{args.trials}] success={ok} benign_reply={replied} steps={len(trajectory)}")

    lo, hi = wilson_ci(successes, args.trials)
    summary = {
        "task": task["id"],
        "model": args.model,
        "trials": args.trials,
        "success": successes,
        "asr": successes / args.trials,
        "asr_ci95": [lo, hi],
        "benign_reply": benign,
        "utility": benign / args.trials,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "rows": rows,
    }

    out = Path("results") / f"batch-{task['id']}-{args.model.replace(':', '_')}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print()
    print(f"task      : {task['id']}")
    print(f"model     : {args.model}")
    print(f"trials    : {args.trials}")
    print(f"success   : {successes}")
    print(f"asr       : {summary['asr']:.3f}  [{lo:.3f}, {hi:.3f}]")
    print(f"utility   : {summary['utility']:.3f}")
    print(f"summary   : {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
