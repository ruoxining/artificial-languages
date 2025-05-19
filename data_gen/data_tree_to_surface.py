"""Extract data to the surface form (the final step)."""
import argparse
import os
import json


def extract_surface(filename: str):
    with open(filename, 'r') as f:
        data = [json.loads(line)['surface'] for line in f.readlines()]

    return data

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract the surface form from the data.")
    parser.add_argument('-i', '--input_file', type=str, required=True)
    parser.add_argument('-o', '--output_file', type=str, required=True)
    args = parser.parse_args()

    formations = ['prefix', 'suffix', 'infix']
    for formation in formations:
        input_path = os.path.join(args.input_file, formation, 'permuted_splits')

        for languagename in os.listdir(input_path):
            for filename in os.listdir(os.path.join(input_path, languagename)):
                output_path = os.path.join(args.output_file, formation, 'permuted_splits', languagename)
                os.makedirs(output_path, exist_ok=True)

                data = extract_surface(os.path.join(input_path, languagename, filename))

                # TODO: examine why a period is missing from the end of the line, during the data generation
                with open(os.path.join(output_path, filename), 'w') as f:
                    for line in data:
                        f.write(line + ' . ' + '\n')
