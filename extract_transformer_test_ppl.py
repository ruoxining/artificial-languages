import os
import re
import csv

ROOT_DIR = "transformer-results"
SUFFIXES = [".0.test.txt", ".1.test.txt", ".2.test.txt"]
PPL_REGEX = r"Perplexity:\s*([0-9.]+)"

# specific directories
settings = ["1-1", "1-2", "1-3",
            # "2-1", "2-2", "2-3",
            "3-1", "3-2",
            "4-1",
            "12-1", "12-2",
            "13-1",
            "5-1", "5-2",
            "6-1", "6-2", "6-3",
            "7-1", "7-2", "7-3",
            "8-1", "8-2",
            "base"]

def extract_perplexity(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    match = re.search(PPL_REGEX, content)
    if match:
        return float(match.group(1))
    else:
        raise ValueError(f"Perplexity not found in {file_path}")

def collect_results():
    results = []
    for setting in settings:
        setting_path = os.path.join(ROOT_DIR, setting)
        if not os.path.isdir(setting_path):
            print(f"Skipping missing directory: {setting_path}")
            continue
        for fname in os.listdir(setting_path):
            if any(fname.endswith(suffix) for suffix in SUFFIXES):
                parts = fname.split(".")  # ['001001', '1', 'test', 'txt']
                if len(parts) < 3:
                    print(f"Unexpected file name format: {fname}")
                    continue
                grammar = parts[0]
                div = parts[1]
                file_path = os.path.join(setting_path, fname)
                try:
                    ppl = extract_perplexity(file_path)
                    results.append((setting, div, grammar, ppl))
                except ValueError as e:
                    print(e)
    return results

def write_csv(results, output_csv):
    with open(output_csv, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["setting", "div", "grammar", "final_ppl"])
        for row in results:
            writer.writerow(row)

if __name__ == "__main__":
    results = collect_results()
    write_csv(results, "transformer_perplexities.csv")
    print("Wrote transformer_perplexities.csv")
