#!/bin/bash

# extract the frequencies of each language
python3 corr/utils/extract_feature.py --input_dir corr/wals --output_dir corr/frequency.csv

# calculate the correlation between the frequencies and the perplexity scores
for sec in base 1-1 1-2 1-3 2-1 2-2 2-3 3-1 3-2 3-3 3-4 4-1 5-1 5-2 6-1 6-2 6-3 7-1 7-2 7-3 8-1 8-2 9-1 9-2 9-3 9-4 12-1 12-2 12-3 12-4 13-1 13-2 13-3 13-4 11-1 11-2 11-3 11-4 12-1 12-2 12-3 12-4 13-1 13-2 13-3 13-4 
do
    python3 corr/utils/calc_correlation.py --ppl_file lstm-results/perplexity_scores.csv --freq_file corr/frequency.csv --section $sec
done
