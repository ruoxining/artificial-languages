"""Extract the perplexity scores from fairseq logs and aggregate into a CSV."""
import argparse
import os
import csv
from typing import Tuple, Optional


def get_train_ppls_from_log(input_file: str) -> Tuple[str, Optional[str], str, str, str, bool]:
    """Extract perplexity scores and metadata from training log file.
    
    Returns:
        Tuple containing (final_ppl, ppl_10, formation, grammar, split, if_finished)
    """
    with open(input_file, 'r') as file:
        all_lines = [l for l in file if len(l.split('|')) > 3]

    ppls = []
    data_dir = None
    if_finished = False
    ppl_10 = None

    for line in all_lines:
        fields = line.split('|')

        for i in range(len(fields)):
            if 'ppl' in fields[i].split():
                ppls.append(fields[i].split()[-1])
                break

        if 'fairseq.data.data_utils' in line:
            data_dir = line.strip().split()[-1]

        if 'epoch 010' in line and 'valid' in line:
            for i in range(len(fields)):
                if 'ppl' in fields[i].split():
                    ppl_10 = fields[i].split()[-1]
                    break

        if 'done training' in line:
            if_finished = True

    if not ppls or not data_dir:
        raise ValueError(f"No perplexity scores or data directory found in the log file: {os.path.abspath(input_file)}")

    final_ppl = ppls[-1]
    parts = data_dir.strip().split('/')
    formation = parts[1]
    grammar = parts[2]
    split = parts[3].split('-')[0]

    return final_ppl, ppl_10, formation, grammar, split, if_finished


def get_test_ppl_from_log(test_file: str) -> str:
    """Extract perplexity score from test log file.
    
    Returns:
        The perplexity score as a string
    """
    with open(test_file, 'r') as file:
        lines = file.readlines()

    if not lines:
        raise ValueError(f"Test file is empty: {os.path.abspath(test_file)}")

    for line in reversed(lines):
        if 'fairseq_cli.eval_lm' in line and 'Perplexity' in line:
            parts = line.strip().split('Perplexity:')
            if len(parts) < 2:
                raise ValueError(f"Perplexity not found in expected format in file: {os.path.abspath(test_file)}")
            ppl = parts[-1].strip()
            return ppl

    raise ValueError(f"Perplexity not found in test file: {os.path.abspath(test_file)}")


def process_train_files(input_dir: str, output_dir: str, prefix: str = '') -> None:
    """Process all training log files in the input directory."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    csv_path = os.path.join(output_dir, "aggregated_ppl.csv")
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['formation', 'grammar', 'div', 'model', 'ppl-10-epochs', 'final_ppl', 'if_finished'])

        for filename in os.listdir(input_dir):
            if not filename.endswith('.out') or (prefix and not filename.startswith(prefix)):
                continue

            try:
                input_file = os.path.join(input_dir, filename)
                final_ppl, ppl_10, formation, grammar, split, is_finished = get_train_ppls_from_log(input_file)
                # Extract model and div from filename (format: model.div.out)
                model = filename.split('.')[0]
                div = filename.split('.')[1] if '.' in filename else split
                writer.writerow([formation, grammar, div, model, ppl_10, final_ppl, is_finished])
            except ValueError as e:
                print(f"Error processing file {filename}: {e}")


def process_test_files(input_dir: str, output_dir: str, model: str, results_dir: str, prefix: str = '') -> None:
    """Process all test log files in the input directory."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    csv_path = os.path.join(output_dir, "aggregated_ppl.csv")
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['formation', 'grammar', 'div', 'model', 'ppl-10-epochs', 'final_ppl', 'if_finished'])

        for filename in os.listdir(input_dir):
            if not filename.endswith('.test.txt') or (prefix and not filename.startswith(prefix)):
                continue

            try:
                test_file = os.path.join(input_dir, filename)
                final_ppl = get_test_ppl_from_log(test_file)

                # Extract formation, grammar, and split from test file
                formation = grammar = split = None
                with open(test_file, 'r') as f:
                    for line in f:
                        if 'loaded' in line and 'examples from:' in line:
                            parts = line.strip().split('examples from:')
                            if len(parts) < 2:
                                raise ValueError(f"Failed to extract dataset path from test log: {os.path.abspath(test_file)}")
                            dataset_path = parts[-1].strip()
                            segments = dataset_path.split('/')
                            if len(segments) < 5:
                                raise ValueError(f"Unexpected dataset path structure in test log: {os.path.abspath(test_file)}")

                            formation = segments[1]
                            grammar = segments[2]
                            split = segments[4]  # last component is "test"
                            break

                if not (formation and grammar and split):
                    raise ValueError(f"Could not extract formation/grammar/split from test log: {os.path.abspath(test_file)}")

                # Extract div from filename (format: model.div.test.txt)
                div = filename.split('.')[1] if '.' in filename else split
                writer.writerow([formation, grammar, div, model, '', final_ppl, ''])
            except ValueError as e:
                print(f"Error processing file {filename}: {e}")


def main():
    parser = argparse.ArgumentParser(description='Extract the perplexity scores from fairseq logs into a CSV.')
    parser.add_argument('-i', '--input_file', type=str, required=True,
        help='Path to input folder containing .out or .test.txt files')
    parser.add_argument('-O', '--output_folder', type=str, required=True,
        help='Location to save output CSV')
    parser.add_argument('-p', '--prefix', type=str, default='',
        help='Optional prefix to filter input files (only process files starting with this prefix)')
    parser.add_argument('--set', choices=['train', 'test'], required=True,
        help='Which set to extract from: train or test')
    parser.add_argument('--results_dir', type=str, default='lstm/results/1-1',
        help='Path to the test results directory (used only if --set test)')
    parser.add_argument('--model', type=str,
        help='Model name to include in CSV (required for test)')

    args = parser.parse_args()

    if args.set == 'test' and not args.model:
        raise ValueError("You must provide --model when --set is 'test'.")

    if args.set == 'train':
        process_train_files(args.input_file, args.output_folder, args.prefix)
    else:
        process_test_files(args.input_file, args.output_folder, args.model, args.results_dir, args.prefix)


if __name__ == '__main__':
    main()
