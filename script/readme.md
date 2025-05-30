# script list

model-sec-exp.sh

## LSTM

base setting:
    hsize           : 512
    embed dim       : 128
    layer           : 2
    data size       : 10k
    epoch           : full (500 currently)
    batch           : 16
    avg sent        : ~ 70 char (max expansion 400, rand seed 0)
    optimizer       : adamw
    scheduler       : inverse sqrt
    vocab size      : 1264
    tokenizer       : sentencepiece

TODO: to move the initial data out of base folder. use 20k as the base directory



1. training data size
    1. 20k
    2. 50k
    3. 100k

2. epoch number
    1. 10
    2. 50
    3. 100

3. batch size
    1. 8
    2. 32

4. optimizer and scheduler (fairseq's adam is like adamw)
    1. adamW + inverse sqrt
    2. adamW + linear

5. layers
    1. 8
    2. 16

6. hsize
    1. 256
    2. 1024

7. embed dim
    1. 256
    2. 512

8. tokenizer
    1. sentencepiece with gold


## Transformer

base setting:
    ffn hsize       : 512
    embed dim       : 128
    decoder input   : 128
    decoder output  : 128
    decoder         : 2
    head            : 2
    data size       : 10k
    epoch           : full (500 currently)
    batch           : 16
    avg sent        : ~ 70 char (max expansion 400, rand seed 0)
    optimizer       : adam
    scheduler       : inverse sqrt
    vocab size      : 512
    tokenizer       : sentencepiece

1. training data size
    1. 20k
    2. 50k
    3. 100k

2. epoch number
    1. 10
    2. 50
    3. 100

3. batch size
    1. 8
    2. 32

4. optimizer and scheduler
    1. adamW + inverse sqrt
    2. adamW + linear

5. decoder layers
    1. 4
    2. 6
    3. 8

6. attention heads
    1. 4
    2. 8
    3. 16

7. ffn hidden size
    1. 256
    2. 1024
    3. 2048

8. embed dim
    1. 256
    2. 512

9. decoder input dim
    1. 512

10. decoder output dim
    1. 512

11. tokenizer
    1. sentencepiece with gold
