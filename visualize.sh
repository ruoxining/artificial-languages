for SECTION in 1-1 1-2 1-3 3-1 3-2 4-1 9-1 5-1 5-2 6-1 6-2 7-1 7-2; do

    python3 extract_fairseq_log.py \
    --input_file lstm-results/$SECTION \
    --output_folder lstm-results/$SECTION \
    --set test \
    --model lstm \
    --results_dir lstm-results/$SECTION

    python3 visualize.py -i lstm-results/$SECTION/aggregated_ppl.csv -o lstm-results/$SECTION

done
