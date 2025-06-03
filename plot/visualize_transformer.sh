#!/bin/bash

# Create output directories
mkdir -p vis

# First extract perplexity scores from all LSTM results
python3 plot/extract_fairseq_log.py \
    --input_file transformer-results \
    --output_folder transformer-results

# Then create visualizations
python3 plot/visualize.py \
    --input_file transformer-results/perplexity_scores.csv \
    --output_folder vis
