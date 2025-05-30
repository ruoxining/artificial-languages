python sample_sentences.py -g base-grammar.gr -n 100000 -O . -b True
python permute_sentences.py -s sample_base-grammar.txt -O permuted_samples/ 
python make_splits.py -S permuted_samples/base -O permuted_splits/base -n 5
python make_splits.py -S permuted_samples/base -O permuted_splits/1-1 -n 10
python make_splits.py -S permuted_samples/base -O permuted_splits/1-2 -n 2
python make_splits.py -S permuted_samples/base -O permuted_splits/1-3 -n 1
