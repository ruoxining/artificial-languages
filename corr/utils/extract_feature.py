"""Extract features from wals dataset and dump to a file."""
import argparse
import os

import pandas as pd


def extract_feature(parameter, attribute, input_dir = 'corr/wals'):
    """Extract features from the wals dataset.

    Args:
        parameter           : parameter of the feature, 82A, 83A, 94A, 85A, 87A, 90A.
        attribute           : attribute of the feature, specific name of the attribute.
        input_dir           : path to the input directory.
    """
    # read in the data
    codes = pd.read_csv(os.path.join(input_dir, "codes.csv"))
    values = pd.read_csv(os.path.join(input_dir, "values.csv"))

    # get merged table
    merged = values.merge(
        codes[['Parameter_ID', 'ID', 'Name']],
        left_on=['Parameter_ID', 'Code_ID'],
        right_on=['Parameter_ID', 'ID'],
        how='left'
    ).rename(columns={'Name': 'Feature_Value'})

    # filter only target features
    filtered = merged[merged['Parameter_ID'] == parameter]

    # group by feature and value, list associated languages
    grouped = filtered.groupby(['Parameter_ID', 'Feature_Value'])['Language_ID'].apply(list)

    # convert to DataFrame for easier reading
    result = grouped.reset_index().rename(columns={'Language_ID': 'Languages'})

    # filter only target attributes
    filtered = result[result['Feature_Value'] == attribute]

    return filtered


def get_n_langs(input_dir='corr/wals'):
    """Get the total number of languages with the target features, excluding feature 94A."""
    # get tables
    codes = pd.read_csv(os.path.join(input_dir, "codes.csv"))
    values = pd.read_csv(os.path.join(input_dir, "values.csv"))

    # get merged table
    merged = values.merge(
        codes[['Parameter_ID', 'ID', 'Name']],
        left_on=['Parameter_ID', 'Code_ID'],
        right_on=['Parameter_ID', 'ID'],
        how='left'
    ).rename(columns={'Name': 'Feature_Value'})

    # exclude feature 94A
    filtered = merged[merged['Parameter_ID'] != '94A']
    
    # get number of languages
    n_langs = filtered['Language_ID'].nunique()

    # only languages with the recorded features
    filtered = filtered[filtered['Language_ID'].notna()]
    n_langs = filtered['Language_ID'].nunique()

    return n_langs


def decode_feature(feature_name, digit):
    """Decode the feature name to a list of languages.
    
    Args:
        feature_name        : name of the feature.
        digit               : digit of the feature, 0 or 1.
    """
    mapping = {
        '82A': {'0': 'SV', '1': 'VS'},
        '83A': {'0': 'OV', '1': 'VO'},
        '94A': {
            '0': 'Final subordinator word',
            '1': 'Initial subordinator word'
        },
        '85A': {'0': 'Postpositions', '1': 'Prepositions'},
        '87A': {'0': 'Adjective-Noun', '1': 'Noun-Adjective'},
        '90A': {
            '0': 'Noun-Relative clause',
            '1': 'Relative clause-Noun'
        }
    }

    # get the mapping for the feature
    attribute = mapping[feature_name][str(digit)]

    # find the language name from wals dataset
    result = extract_feature(feature_name, attribute)
    if result.empty or result['Languages'].iloc[0] == []:
        return set()
    
    languages = set(result['Languages'].iloc[0])
    return languages


def calc_frequency(language_name, input_dir):
    """Calculate the frequency of a given language name, ignoring feature 3 (94A).

    Args:
        language_name       : name of the language in the wals dataset.
        input_dir           : path to the input directory.
    """
    # digit to feature name mapping
    target_features = {
        '1': '82A',
        '2': '83A',
        '3': '94A',  # This will be ignored
        '4': '85A',
        '5': '87A',
        '6': '90A'
    }

    language_digits = [int(digit) for digit in language_name]

    langs = []
    for i, digit in enumerate(language_digits):
        # Skip feature 3 (index 2)
        if i == 2:
            continue
        feature = target_features[str(i+1)]
        lang_set = decode_feature(feature, digit)
        langs.append(lang_set)

    # If we have any language sets, find their intersection
    if langs:
        langs = set.intersection(*langs)
    else:
        langs = set()

    # get number of languages in this parameter
    n_langs = get_n_langs(input_dir)
    # calculate frequency
    frequency = len(langs) / n_langs

    return frequency


# TODO: find out how the previous paper get the frequencies of missing languages

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Extract features from wals dataset.')
    parser.add_argument('--input_dir', '-i', type=str, help='input directory', default='corr/wals')
    parser.add_argument('--output_dir', '-o', type=str, help='output directory', default='corr/frequency.csv')
    args = parser.parse_args()

    # get language names
    language_names = [f'{i:06b}' for i in range(0, 64)]

    # calculate frequency for each language
    frequencies = []
    for language_name in language_names:
        frequency = calc_frequency(language_name, args.input_dir)
        frequencies.append(frequency)

    # save to csv
    df = pd.DataFrame(frequencies, index=language_names, columns=['frequency'])
    df.index.name = 'grammar'
    df.to_csv(args.output_dir, index=True)
