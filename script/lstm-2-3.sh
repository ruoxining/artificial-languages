#!/bin/bash
#SBATCH --output=logs/%x_%j.out
#SBATCH --mem=4G
#SBATCH --cpus-per-task=20
#SBATCH --qos=m5
#SBATCH --gres=gpu:1
#SBATCH --time=1:00:00
#SBATCH --mail-type=END,FAIL,TIME_LIMIT
#SBATCH --mail-user=ruoxining@outlook.com

GRAMMAR=$1
SPLIT=$2

mkdir -p "data-bin/base/${GRAMMAR}/${SPLIT}-dataset"
mkdir -p "checkpoints/2-3/${GRAMMAR}/${SPLIT}-lstm"
mkdir -p "lstm-results/2-3"
mkdir -p "sentence_scores_lstm/2-3"

# Base settings:
# - hsize: 512
# - embed dim: 128
# - layer: 2
# - data size: 10k
# - epoch: full (500)
# - batch: 4
# - optimizer: adam
# - scheduler: inverse sqrt
# - vocab size: 512
# - tokenizer: sentencepiece

fairseq-preprocess --only-source \
    --trainpref "data_gen/permuted_splits/base/${GRAMMAR}/${SPLIT}.trn" \
    --validpref "data_gen/permuted_splits/base/${GRAMMAR}/${SPLIT}.dev" \
    --testpref "data_gen/permuted_splits/base/${GRAMMAR}/${SPLIT}.tst" \
    --destdir "data-bin/base/${GRAMMAR}/${SPLIT}-dataset" \
    --workers 20

fairseq-train --task language_modeling "data-bin/base/${GRAMMAR}/${SPLIT}-dataset" \
    --save-dir "checkpoints/2-3/${GRAMMAR}/${SPLIT}-lstm" \
    --arch lstm_lm \
    --share-decoder-input-output-embed \
    --dropout 0.3 \
    --optimizer adam \
    --adam-betas '(0.9,0.98)' \
    --weight-decay 0.01 \
    --lr 0.0005 \
    --lr-scheduler inverse_sqrt \
    --warmup-updates 4000 \
    --clip-norm 0.0 \
    --warmup-init-lr 1e-07 \
    --tokens-per-sample 512 \
    --sample-break-mode none \
    --max-tokens 2048 \
    --update-freq 16 \
    --patience 5 \
    --max-update 10000 \
    --no-epoch-checkpoints \
    --no-last-checkpoints \
    --decoder-layers 2 \
    --decoder-embed-dim 128 \
    --decoder-out-embed-dim 128 \
    --decoder-hidden-size 512 \
    --max-epoch 100

fairseq-eval-lm "data-bin/base/${GRAMMAR}/${SPLIT}-dataset" \
    --path "checkpoints/2-3/${GRAMMAR}/${SPLIT}-lstm/checkpoint_best.pt" \
    --tokens-per-sample 512 \
    --gen-subset "valid" \
    --output-word-probs \
    --quiet 2> "lstm-results/2-3/${GRAMMAR}.${SPLIT}.dev.txt"

fairseq-eval-lm "data-bin/base/${GRAMMAR}/${SPLIT}-dataset" \
    --path "checkpoints/2-3/${GRAMMAR}/${SPLIT}-lstm/checkpoint_best.pt" \
    --tokens-per-sample 512 \
    --gen-subset "test" \
    --output-word-probs \
    --quiet 2> "lstm-results/2-3/${GRAMMAR}.${SPLIT}.test.txt"

python get_sentence_scores.py -i "lstm-results/2-3/${GRAMMAR}.${SPLIT}.test.txt" -O "sentence_scores_lstm/2-3/"
