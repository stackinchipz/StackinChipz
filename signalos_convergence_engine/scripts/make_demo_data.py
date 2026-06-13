from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from signalos.data_sources.demo import write_demo_data
from signalos.data_sources.fundamentals import write_demo_fundamentals


if __name__ == "__main__":
    out = ROOT / "data" / "demo"
    write_demo_data(out)
    f = write_demo_fundamentals(out)
    print(f"Wrote demo data to {out}")
    print(f"Wrote demo fundamentals to {f}")
