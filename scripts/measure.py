import time
import tracemalloc
from pathlib import Path

# # Додаємо корінь проєкту / папку src до шляхів пошуку модулів
# sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from procure_stat.sources.json_file import read_rows_jsonl  # type: ignore

path = Path("data/large.jsonl")

for lazy in (True, False):
    tracemalloc.start()
    t0 = time.perf_counter()

    rows = read_rows_jsonl(path) if lazy else list(read_rows_jsonl(path))
    total = sum(1 for _ in rows)

    peak = tracemalloc.get_traced_memory()[1] / 1024 / 1024
    tracemalloc.stop()

    mode = "генератор" if lazy else "список"
    print(f"{mode}: {total} записів, {time.perf_counter() - t0:.2f} с, пік {peak:.1f} МБ")
