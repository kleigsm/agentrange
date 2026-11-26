from __future__ import annotations

import glob
import json


def main() -> None:
    files = sorted(glob.glob("results/batch-email-exfil-003-*.json"))
    if not files:
        print("no batch files yet")
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
