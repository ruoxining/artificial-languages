"""Extract the perplexity scores from fairseq and aggregate into a CSV."""
import argparse
import os
import csv


def get_all_from_log(input_file: str):
    with open(input_file, 'r') as file:
        all_lines = [l for l in file if len(l.split('|')) > 3]

    ppls = []
    data_dir = None
    if_finished = False

    for line in all_lines:
        fields = line.split('|')

        for i in range(len(fields)):
            if 'ppl' in fields[i].split():
                ppls.append(fields[i].split()[-1])

        if 'fairseq.data.data_utils' in line:
            data_dir = line.strip().split()[-1]

        if 'done training' in line:
            if_finished = True

    if not ppls or not data_dir:
        raise ValueError("No perplexity scores or data directory found in the log file.")

    final_ppl = ppls[-1]
    parts = data_dir.strip().split('/')
    formation = parts[1]
    grammar = parts[2]
    split = parts[3].split('-')[0]

    return final_ppl, ppl_10, formation, grammar, split, if_finished


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract the perplexity scores from fairseq logs into a CSV.")
    parser.add_argument("-i", "--input_file", type=str, required=True,
        help="Path to input folder containing .out files")
    parser.add_argument("-O", "--output_folder", type=str, required=True,
        help="Location to save output CSV")
    args = parser.parse_args()

    if not os.path.exists(args.output_folder):
        os.makedirs(args.output_folder)

    csv_path = os.path.join(args.output_folder, "aggregated_ppl.csv")
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['formation', 'grammar', 'div', 'model', 'ppl-10-epochs', 'final_ppl', 'if_finished'])

        for filename in os.listdir(args.input_file):
            if filename.endswith('.out'):
                try:
                    input_file = os.path.join(args.input_file, filename)
                    final_ppl, ppl_10, formation, grammar, split, is_finished = get_all_from_log(input_file)
                    model = filename.split('-')[0].split('_')[-1]
                    writer.writerow([formation, grammar, split, model, ppl_10, final_ppl, is_finished])
                except ValueError as e:
                    print(f"Error processing file {filename}: {e}")
