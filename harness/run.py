from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from defenses import build_defense
from envs.email_assistant.agent import run_agent
from envs.email_assistant.store import Mailbox
from harness.clients import load_env, make_client_factory
from harness.oracle import canary_in_sink, exposed_to_attack
from harness.tools_builder import build_tools


def main() -> int:
    load_env()

    parser = argparse.ArgumentParser(description="Run one AgentRange task.")
    parser.add_argument("--task", required=True)
    parser.add_argument("--model", default="scripted")
    parser.add_argument("--defense", default="none")
    parser.add_argument("--out", default="results/evidence")
    args = parser.parse_args()

    task_path = Path(args.task)
    task = yaml.safe_load(task_path.read_text(encoding="utf-8"))
    state = json.loads(Path(task["state"]).read_text(encoding="utf-8"))

    db_path = Path("results") / f"{task['id']}.db"
    if db_path.exists():
        db_path.unlink()
    mailbox = Mailbox(db_path)
    mailbox.seed(state)

    client = make_client_factory(args.model, state["canary"])()
    defense = build_defense(args.defense)
    trajectory = run_agent(
        mailbox,
        client,
        task["goal"],
        defense=defense,
        tools=build_tools(task),
    )
    sent = mailbox.sent()
    mailbox.close()
    verdict = canary_in_sink(
        trajectory, state["canary"], "send_email", sent=sent
    )
    exposed = exposed_to_attack(trajectory, task)
    if verdict["success"]:
        outcome = "attacked"
    elif exposed:
        outcome = "defended"
    else:
        outcome = "not_exposed"

    evidence = {
        "spec": "agentrange/evidence@0.1",
        "id": task["id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "target": {
            "framework": "raw",
            "model": args.model,
            "defense": args.defense,
            "env": "email_assistant@0.1",
        },
        "task": {"id": task["id"], "goal": task["goal"]},
        "canary": state["canary"],
        "trajectory": trajectory,
        "oracle": {
            "type": "canary_in_sink",
            "sink": "send_email",
            "canary": state["canary"],
        },
        "verdict": {
            "reproduced": verdict["success"],
            "exposed": exposed,
            "outcome": outcome,
            "trials": 1,
            "success": int(verdict["success"]),
        },
        "sent": sent,
    }

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{task['id']}.json"
    out_path.write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"task      : {task['id']}")
    print(f"model     : {args.model}")
    print(f"steps     : {len(trajectory)}")
    print(f"canary    : {state['canary']}")
    print(f"attacked  : {verdict['success']}")
    print(f"sent      : {len(sent)} email(s)")
    for item in sent:
        print(f"  -> {item['to_addr']} | {item['subject']}")
    print(f"evidence  : {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
