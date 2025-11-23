import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)                   
sys.path.append(root_dir)
import time
import random
from datetime import datetime as dt, timedelta
from Src.Core.prototype import prototype
from Src.Models.transaction_model import transaction_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model
from Src.Models.storage_model import storage_model

def run_load_test():
    noms = [nomenclature_model.create(f"Nom{i}", group_model(), range_model.create("unit", 1, None)) for i in range(50)]
    for i, n in enumerate(noms): 
        n.unique_code = f"nom{i}"
    storages = [storage_model() for _ in range(10)]
    for i, s in enumerate(storages): 
        s.unique_code = f"stor{i}"
    transactions = []
    start_dt = dt(1900, 1, 1)
    for i in range(10000):
        t = transaction_model()
        t.nomenclature = random.choice(noms)
        t.storage = random.choice(storages)
        t.range = t.nomenclature.range
        t.value = random.uniform(-100, 100)
        t.period = start_dt + timedelta(days=random.randint(0, 365*100))
        t.unique_code = f"t{i}"
        transactions.append(t)

    target_date = dt(2024, 10, 1).date()
    results = []
    for block_str in ["1900-01-01", "2000-01-01", "2020-01-01", "2023-01-01"]:
        block_date = dt.strptime(block_str, "%Y-%m-%d").date()
        start = time.time()
        osv_block = prototype.generate_osv_up_to_block(transactions, block_date)
        prototype.save_blocked_osv(osv_block, "load_blocked.json")
        prototype.generate_osv_with_block(transactions, target_date, block_date)
        elapsed = time.time() - start
        results.append(f"| {block_str} | {elapsed:.4f} |")

    with open("load_test_results.md", "w", encoding="utf-8") as f:
        f.write("# Load Test Results\n| Block Period | Time (s) |\n|---|----|\n" + "\n".join(results))
    
    print("ГОТОВО! Файл load_test_results.md")

if __name__ == "__main__":
    run_load_test()