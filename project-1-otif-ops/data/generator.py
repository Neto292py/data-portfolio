# generator.py  -- creates synthetic_small.csv (~5k) and synthetic_medium.csv (~50k)
# Stdlib only. Reproducible with fixed seed.

import csv, random, argparse
from datetime import date, timedelta

SEED = 42
CATEGORIES = {
    "Electronics": (80, 300),
    "Home": (15, 120),
    "Sports": (20, 180),
    "Toys": (10, 60),
}
REGIONS = ["North", "South", "East", "West"]
WAREHOUSES = ["WH-A", "WH-B", "WH-C", "WH-D"]
DEFECT_TYPES = ["Damaged", "Wrong Item", "Missing Parts", "Other"]

def rand_date(start: date, days_range: int) -> date:
    return start + timedelta(days=random.randint(0, days_range))

def clamp(v, lo, hi):
    return max(lo, min(v, hi))

def generate_rows(n_rows: int):
    random.seed(SEED)
    rows = []
    start = date(2024, 1, 1)
    for i in range(1, n_rows + 1):
        order_id = f"O{i:07d}"
        order_dt = rand_date(start, 365)
        shipping_method = random.choices(["Standard", "Expedited"], weights=[0.7, 0.3])[0]
        sla_days = 5 if shipping_method == "Standard" else 2

        customer_id = f"C{random.randint(1, 2500):05d}"
        region = random.choice(REGIONS)
        prod_cat = random.choice(list(CATEGORIES.keys()))
        price_lo, price_hi = CATEGORIES[prod_cat]
        unit_price = round(random.uniform(price_lo, price_hi), 2)
        product_id = f"P{random.randint(1, 800):05d}"
        warehouse_id = random.choice(WAREHOUSES)

        units_ordered = clamp(int(random.gauss(3, 2)), 1, 12)
        if random.random() < 0.05:
            units_shipped = clamp(units_ordered - random.randint(1, min(2, units_ordered)), 1, units_ordered)
        else:
            units_shipped = units_ordered

        discount_rate = round(random.uniform(0.05, 0.30), 2) if random.random() < 0.2 else 0.0

        promised_date = order_dt + timedelta(days=sla_days)

        late_prob = 0.18 if shipping_method == "Standard" else 0.08
        base = random.randint(1, sla_days + 1)
        if random.random() < late_prob:
            base += random.randint(1, 5)
        lead_time_days = base
        deliver_date = order_dt + timedelta(days=lead_time_days)

        ship_delay = clamp(int(random.gauss(1, 1)), 0, lead_time_days)
        ship_date = order_dt + timedelta(days=ship_delay)

        late_days = max((deliver_date - promised_date).days, 0)
        in_full_flag = 1 if units_shipped == units_ordered else 0
        on_time_flag = 1 if deliver_date <= promised_date else 0
        otif_flag = 1 if (on_time_flag and in_full_flag) else 0

        defect_flag = 1 if random.random() < 0.03 else 0
        defect_type = random.choice(DEFECT_TYPES) if defect_flag else ""
        return_flag = 1 if random.random() < 0.02 else 0

        revenue = round(units_shipped * unit_price * (1 - discount_rate), 2)

        rows.append({
            "order_id": order_id,
            "order_date": order_dt.isoformat(),
            "promised_date": promised_date.isoformat(),
            "ship_date": ship_date.isoformat(),
            "deliver_date": deliver_date.isoformat(),
            "customer_id": customer_id,
            "region": region,
            "product_id": product_id,
            "category": prod_cat,
            "units_ordered": units_ordered,
            "units_shipped": units_shipped,
            "unit_price": unit_price,
            "discount_rate": discount_rate,
            "shipping_method": shipping_method,
            "warehouse_id": warehouse_id,
            "defect_flag": defect_flag,
            "defect_type": defect_type,
            "return_flag": return_flag,
            "lead_time_days": lead_time_days,
            "late_days": late_days,
            "in_full_flag": in_full_flag,
            "otif_flag": otif_flag,
            "revenue": revenue
        })
    return rows

def write_csv(path: str, rows):
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

def main():
    small = generate_rows(5000)
    write_csv("synthetic_small.csv", small)
    medium = generate_rows(50000)
    write_csv("synthetic_medium.csv", medium)
    print("Wrote synthetic_small.csv (~5k) and synthetic_medium.csv (~50k).")

if __name__ == "__main__":
    _ = argparse.ArgumentParser(description="Generate synthetic OTIF operations data.").parse_args()
    main()
