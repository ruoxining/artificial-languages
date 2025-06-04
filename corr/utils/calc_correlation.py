"""Calculate correlation between features and perplexity, report a significance."""
import argparse
import json
import os
from typing import Tuple, Dict, Any

import pandas as pd
from scipy import stats


def calc_correlation(ppl_df: pd.DataFrame, freq_df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate correlation between features and perplexity, report a significance."""
    # merge on marginalized_grammar
    merged = ppl_df.merge(
        freq_df,
        on='marginalized_grammar',
        how='inner'
    )

    # sanity check: make sure columns exist
    if 'perplexity' not in merged.columns or 'frequency' not in merged.columns:
        raise ValueError('Merged dataframe missing required columns.')

    if len(merged) < 2:
        raise ValueError('Not enough data after merging to calculate correlation.')

    # Calculate pearson correlation
    correlation, p_value = stats.pearsonr(merged['perplexity'], merged['frequency'])

    return {
        'correlation': float(correlation),
        'p_value': float(p_value),
        'n_samples': int(len(merged))
    }


def read_data(ppl_file: str, freq_file: str, section: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    ppl_df = pd.read_csv(ppl_file)
    ppl_df = ppl_df[ppl_df['setting'] == section]
    freq_df = pd.read_csv(freq_file)

    # normalize grammar column
    ppl_df['grammar'] = ppl_df['grammar'].apply(lambda x: format(int(x), '06b'))
    freq_df['grammar'] = freq_df['grammar'].apply(lambda x: format(int(x), '06b'))

    # marginalize digit 3
    ppl_df['marginalized_grammar'] = ppl_df['grammar'].apply(lambda x: x[:2] + 'x' + x[3:])
    freq_df['marginalized_grammar'] = freq_df['grammar'].apply(lambda x: x[:2] + 'x' + x[3:])

    # aggregate
    ppl_df = ppl_df.groupby('marginalized_grammar')['perplexity'].mean().reset_index()
    freq_df = freq_df.groupby('marginalized_grammar')['frequency'].mean().reset_index()

    return ppl_df, freq_df


if __name__ == '__main__':
    """Main function to process command line arguments and run correlation analysis."""
    parser = argparse.ArgumentParser('Calculate correlation between features and perplexity, report a significance.')
    parser.add_argument('--ppl_file', type=str, required=True, help='input file with perplexity scores')
    parser.add_argument('--freq_file', type=str, required=True, help='input file with frequency scores')
    parser.add_argument('--section', type=str, required=True, help='section to analyze (e.g., "1-1", "2-1", etc.)')
    args = parser.parse_args()

    # read data
    ppl_df, freq_df = read_data(args.ppl_file, args.freq_file, args.section)

    # calc correlation
    results = calc_correlation(ppl_df, freq_df)
    results['setting'] = args.section

    # dump to jsonl
    with open(os.path.join('corr', 'corr.jsonl'), 'a') as outfile:
        outfile.write(json.dumps(results))
        outfile.write('\n')
    # dump to jsonl
