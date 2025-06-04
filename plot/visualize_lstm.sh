#!/bin/bash

# Create output directories
mkdir -p vis

# First extract perplexity scores from all LSTM results
python3 plot/extract_fairseq_log.py \
    --input_file lstm-results \
    --output_folder lstm-results

# Then create visualizations
python3 plot/visualize.py \
    --input_file lstm-results/perplexity_scores.csv \
    --output_folder vis
