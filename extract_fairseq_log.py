"""Extract the perplexity scores from fairseq logs and aggregate into a CSV."""
import argparse
import os
import csv


def get_train_ppls_from_log(input_file: str):
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
        raise ValueError("No perplexity scores or data directory found in the log file.")

    final_ppl = ppls[-1]
    parts = data_dir.strip().split('/')
    formation = parts[1]
    grammar = parts[2]
    split = parts[3].split('-')[0]

    return final_ppl, ppl_10, formation, grammar, split, if_finished


def get_test_ppl_from_log(test_file: str):
    with open(test_file, 'r') as file:
        lines = file.readlines()

    if not lines:
        raise ValueError("Test file is empty.")

    for line in reversed(lines):
        if 'fairseq_cli.eval_lm' in line and 'Perplexity' in line:
            parts = line.strip().split('Perplexity:')
            if len(parts) < 2:
                raise ValueError("Perplexity not found in expected format.")
            ppl = parts[-1].strip()
            return ppl

    raise ValueError("Perplexity not found in test file.")


if __name__ == '__main__':
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

    if not os.path.exists(args.output_folder):
        os.makedirs(args.output_folder)

    csv_path = os.path.join(args.output_folder, "aggregated_ppl.csv")
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['formation', 'grammar', 'div', 'model', 'ppl-10-epochs', 'final_ppl', 'if_finished'])

        for filename in os.listdir(args.input_file):
            if args.set == 'train':
                if not filename.endswith('.out') or (args.prefix and not filename.startswith(args.prefix)):
                    continue
            elif args.set == 'test':
                if not filename.endswith('.test.txt') or (args.prefix and not filename.startswith(args.prefix)):
                    continue

            try:
                if args.set == 'train':
                    input_file = os.path.join(args.input_file, filename)
                    final_ppl, ppl_10, formation, grammar, split, is_finished = get_train_ppls_from_log(input_file)
                    model = filename.split('-')[0].split('_')[-1]
                else:
                    test_file = os.path.join(args.input_file, filename)
                    final_ppl = get_test_ppl_from_log(test_file)

                    if args.set == 'train':
                        parts = args.results_dir.strip().split('/')
                        if len(parts) < 3:
                            raise ValueError("Unexpected format of results_dir")

                        formation = parts[1]
                        grammar = parts[2]
                        split = os.path.basename(args.results_dir).split('-')[0]
                    else:
                        formation = grammar = split = None

                        with open(test_file, 'r') as f:
                            for line in f:
                                if 'loaded' in line and 'examples from:' in line:
                                    parts = line.strip().split('examples from:')
                                    if len(parts) < 2:
                                        raise ValueError("Failed to extract dataset path from test log.")
                                    dataset_path = parts[-1].strip()
                                    segments = dataset_path.split('/')
                                    if len(segments) < 5:
                                        raise ValueError("Unexpected dataset path structure in test log.")

                                    # Expecting path like: data-bin/1-1/011010/0-dataset/test
                                    formation = segments[1]
                                    grammar = segments[2]
                                    split = segments[4]  # last component is "test", no -split used
                                    break

                        if not (formation and grammar and split):
                            raise ValueError("Could not extract formation/grammar/split from test log.")


                    model = args.model
                    ppl_10 = ''
                    is_finished = ''

                writer.writerow([formation, grammar, split, model, ppl_10, final_ppl, is_finished])

            except ValueError as e:
                print(f"Error processing file {filename}: {e}")
