"""Extract perplexity scores from fairseq test outputs."""
import argparse
import os
import re
import csv

SUFFIXES = [".0.test.txt", ".1.test.txt", ".2.test.txt"]
PPL_REGEX = r"Perplexity:\s*([0-9.]+)"

# specific directories
settings = {
    "lstm": ["1-1", "1-2", "1-3",
             "2-1", "2-2", "2-3",
             "3-1", "3-2",
             "4-1",
             "5-1", "5-2",
             "6-1", "6-2", "6-3",
             "7-1", "7-2", "7-3",
             "8-1", "8-2",
             "base"],
    "transformer": ["1-1", "1-2", "1-3",
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
    }


def extract_perplexity(file_path):
    """Extract perplexities from a single file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        match = re.search(PPL_REGEX, content)
        if match:
            return float(match.group(1))
        else:
            print(f"Warning: Perplexity not found in {file_path}")
            return None
    except Exception as e:
        print(f"Error reading {file_path}: {str(e)}")
        return None


def collect_results(input_file):
    """Collect perplexity scores from all files in the input directory."""
    results = []
    model_type = "lstm" if "lstm" in input_file else "transformer"
    
    for setting in settings[model_type]:
        setting_path = os.path.join(input_file, setting)
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
                
                ppl = extract_perplexity(file_path)
                if ppl is not None:
                    results.append((setting, div, grammar, ppl))
    
    if not results:
        raise ValueError("No valid perplexity scores found in any files")
        
    return results


def write_csv(results, output_csv):
    """Write extracted results to a CSV file."""
    with open(output_csv, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["setting", "div", "grammar", "perplexity"])
        for row in results:
            writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser('Extract perplexity scores from fairseq test outputs.')
    parser.add_argument('--input_file', type=str, required=True, help='input directory', choices=['lstm-results', 'transformer-results'])
    parser.add_argument('--output_folder', type=str, required=True, help='output folder', default='vis')
    args = parser.parse_args()

    try:
        results = collect_results(args.input_file)
        output_path = os.path.join(args.output_folder, "perplexity_scores.csv")
        write_csv(results, output_path)
        print(f"Successfully wrote {len(results)} perplexity scores to {output_path}")
    except Exception as e:
        print(f"Error: {str(e)}")
        raise
