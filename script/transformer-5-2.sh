#!/bin/bash
#SBATCH --output=logs/%x_%j.out
#SBATCH --mem=4G
#SBATCH --cpus-per-task=1
#SBATCH --qos=m5
#SBATCH --gres=gpu:1
#SBATCH --time=1:00:00
#SBATCH --mail-type=FAIL,TIME_LIMIT
#SBATCH --mail-user=ruoxining@outlook.com

GRAMMAR=$1
SPLIT=$2

mkdir -p "data-bin/base/${GRAMMAR}/${SPLIT}-dataset"
mkdir -p "checkpoints/5-2/${GRAMMAR}/${SPLIT}-transformer"
mkdir -p "transformer-results/5-2"
mkdir -p "sentence_scores_transformer/5-2"

# 5-2 settings:
# - ffn hsize: 512
# - embed dim: 128
# - decoder input: 128
# - decoder output: 128
# - decoder: 6
# - head: 2
# - data size: 20k
# - epoch: full (500)
# - batch: 16
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

# Build the fairseq-train command
TRAIN_CMD="fairseq-train --task language_modeling \"data-bin/base/${GRAMMAR}/${SPLIT}-dataset\" \
    --save-dir \"checkpoints/5-2/${GRAMMAR}/${SPLIT}-transformer\" \
    --arch transformer_lm \
    --share-decoder-input-output-embed \
    --dropout 0.3 \
    --attention-dropout 0.1 \
    --decoder-input-dim 128 \
    --decoder-output-dim 128 \
    --decoder-normalize-before \
    --optimizer adam \
    --adam-betas '(0.9,0.98)' \
    --weight-decay 0.01 \
    --lr 0.0005 \
    --lr-scheduler inverse_sqrt \
    --warmup-updates 400 \
    --clip-norm 0.0 \
    --warmup-init-lr 1e-07 \
    --tokens-per-sample 128 \
    --sample-break-mode none \
    --max-tokens 512 \
    --update-freq 4 \
    --patience 5 \
    --max-update 10000 \
    --no-epoch-checkpoints \
    --no-last-checkpoints \
    --decoder-layers 6 \
    --decoder-embed-dim 128 \
    --decoder-output-dim 128 \
    --decoder-ffn-embed-dim 512 \
    --decoder-attention-heads 2 \
    --fp16"

# Add restore-file parameter if checkpoint exists
if [ -f "checkpoints/5-2/${GRAMMAR}/${SPLIT}-transformer/checkpoint_last.pt" ]; then
    TRAIN_CMD="$TRAIN_CMD --restore-file \"checkpoints/5-2/${GRAMMAR}/${SPLIT}-transformer/checkpoint_last.pt\""
fi

# Execute the training command
eval $TRAIN_CMD

fairseq-eval-lm "data-bin/base/${GRAMMAR}/${SPLIT}-dataset" \
    --path "checkpoints/5-2/${GRAMMAR}/${SPLIT}-transformer/checkpoint_best.pt" \
    --tokens-per-sample 128 \
    --gen-subset "valid" \
    --output-word-probs \
    --quiet 2> "transformer-results/5-2/${GRAMMAR}.${SPLIT}.dev.txt"

fairseq-eval-lm "data-bin/base/${GRAMMAR}/${SPLIT}-dataset" \
    --path "checkpoints/5-2/${GRAMMAR}/${SPLIT}-transformer/checkpoint_best.pt" \
    --tokens-per-sample 128 \
    --gen-subset "test" \
    --output-word-probs \
    --quiet 2> "transformer-results/5-2/${GRAMMAR}.${SPLIT}.test.txt"

python get_sentence_scores.py -i "transformer-results/5-2/${GRAMMAR}.${SPLIT}.test.txt" -O "sentence_scores_transformer/5-2/" 
