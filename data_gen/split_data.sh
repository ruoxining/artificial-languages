python3 data_gen/make_splits.py -S data-train/infix/sent_permuted -O data-train/infix/permuted_splits --num_splits 5
python3 data_gen/make_splits.py -S data-train/prefix/sent_permuted -O data-train/prefix/permuted_splits --num_splits 5
python3 data_gen/make_splits.py -S data-train/suffix/sent_permuted -O data-train/suffix/permuted_splits --num_splits 5

python3 data_gen/data_tree_to_surface.py -i data-train -o data-train
