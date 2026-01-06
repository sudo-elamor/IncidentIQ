import csv

def read_loghub_csv(csv_path, dataset):
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["_dataset"] = dataset  
            rows.append(row)
    return rows
