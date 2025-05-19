"""Filter out a minimal portion of training data that makes the factors balanced: 5 factors * 6 permutations."""
import argparse
import os
import shutil


def filter_data(input_dir: str, output_dir: str) -> None:
    """."""
    # check if dirs exist and data format ok
    assert os.path.exists(input_dir), f"Input directory {input_dir} does not exist."
    for filename in os.listdir(input_dir):
        assert len(filename.split('.')[0].split('-')) == 2, f'no 7 digits or svo name'
        assert filename.split('.')[0].split('-')[0][1:].isnumeric(), f'no 7 digits'
        assert filename.split('.')[0].split('-')[1] in ['SVO', 'SOV', 'VSO', 'VOS', 'OVS', 'OSV'], f'no svo name'
    os.makedirs(output_dir, exist_ok=True)

    # filter the files
    seven_digit_names = []
    lang = 1
    for i in range(5):
        seven_digit_names.append(f'g{lang<<i:07b}')

    svo_names = ['SVO', 'SOV', 'VSO', 'VOS', 'OVS', 'OSV']

    for digit_name in seven_digit_names:
        for svo_name in svo_names:
            # check if the file exists
            filename = f'{digit_name}-{svo_name}.txt'
            filepath = os.path.join(input_dir, filename)
            shutil.copy(filepath, os.path.join(output_dir, filename))

    print(f"Filtered data saved to {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str, default='data-train-adjust')
    parser.add_argument('--output_dir', type=str, default='data-train-adjust-filtered')
    args = parser.parse_args()

    # TODO: remember to change the folder to be filtered to divided data

    formations = ['infix', 'suffix', 'prefix']
    for formation in formations:
        input_dir = os.path.join(args.input_dir, formation, 'sent_permuted')
        output_dir = os.path.join(args.output_dir, formation, 'sent_permuted')
        os.makedirs(output_dir, exist_ok=True)
        print(f"Filtering data from {input_dir} to {output_dir}")
        filter_data(input_dir, output_dir)
