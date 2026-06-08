"""Runner test không cần pytest (pip bị chặn mạng).

Chạy: python tests/run.py — gọi mọi hàm test_* trong tests/test_*.py.
Tương thích pytest sau (cùng các hàm test_*).
"""

import importlib
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


def main() -> int:
    test_files = sorted(p for p in (ROOT / "tests").glob("test_*.py"))
    passed = failed = 0
    for f in test_files:
        mod = importlib.import_module(f"tests.{f.stem}")
        for name in sorted(dir(mod)):
            if name.startswith("test_") and callable(getattr(mod, name)):
                try:
                    getattr(mod, name)()
                    passed += 1
                    print(f"PASS {f.stem}.{name}")
                except Exception:
                    failed += 1
                    print(f"FAIL {f.stem}.{name}")
                    traceback.print_exc()
    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
