SECTION=$1

python extract_fairseq_log.py \
  --input_file lstm-results/$SECTION \
  --output_folder lstm-results/$SECTION \
  --set test \
  --model lstm \
  --results_dir lstm-results/$SECTION

python3 visualize.py -i lstm-results/$SECTION/aggregated_ppl.csv
