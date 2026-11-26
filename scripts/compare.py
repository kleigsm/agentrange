from __future__ import annotations

import glob
import json
import sys


def main() -> None:
    task = sys.argv[1] if len(sys.argv) > 1 else "004"
    files = sorted(glob.glob(f"results/batch-email-exfil-{task}-*.json"))
    if not files:
        print(f"no batch files for task {task}")
        return
    print(f"{'defense':<22}{'ASR':>8}{'exposed':>9}{'utility':>9}{'trials':>8}")
    for path in files:
        d = json.load(open(path, encoding="utf-8"))
        print(
            f"{d['defense']:<22}{d['asr']:>8.3f}"
            f"{d['exposure_rate']:>9.3f}{d['utility']:>9.3f}{d['trials']:>8}"
        )


if __name__ == "__main__":
    main()
