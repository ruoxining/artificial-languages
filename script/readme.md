# script list

model-sec-exp.sh

## LSTM

base setting:
    hsize           : 512
    embed dim       : 128
    layer           : 2
    data size       : 20k
    epoch           : full (500 currently)
    batch           : 16
    avg sent        : ~ 70 char (max expansion 400, rand seed 0)
    optimizer       : adamw
    scheduler       : inverse sqrt
    vocab size      : 1264
    tokenizer       : sentencepiece

1. training data size (*)
    1. 10k
    2. 50k
    3. 100k

2. epoch number
    1. 10
    2. 50
    3. 100

3. batch size
    1. 8
    2. 32
    3. 64
    4. 128

4. optimizer and scheduler (fairseq's adam is implemented as adamw)
    1. adamW + linear

5. layers (*)
    1. 8
    2. 16

6. hsize (*)
    1. 256
    2. 1024
    3. 128

7. embed dim (*)
    1. 256
    2. 512
    3. 1024

8. tokenizer
    1. sentencepiece with gold

9. dropout (*)
    1. 0
    2. 0.1
    3. 0.2
    4. 0.3

10. max expansion
    1. 50
    2. 800

## Transformer

base setting:
    ffn hsize       : 512
    embed dim       : 128
    decoder input   : 128
    decoder output  : 128
    decoder         : 2
    head            : 2
    data size       : 20k
    epoch           : full (500 currently)
    batch           : 16
    avg sent        : ~ 70 char (max expansion 400, rand seed 0)
    optimizer       : adam
    scheduler       : inverse sqrt
    vocab size      : 512
    tokenizer       : sentencepiece

1. training data size (*)
    1. 10k
    2. 50k
    3. 100k

2. epoch number
    1. 10
    2. 50
    3. 100

3. batch size
    1. 8
    2. 32
    3. 64
    4. 128

4. optimizer and scheduler
    2. adamW + linear

5. decoder layers (*)
    1. 4
    2. 6
    3. 8
    4. 12
    5. 16
    6. 32

6. attention heads
    1. 4
    2. 8
    3. 16
    4. 12

7. ffn hidden size
    1. 256
    2. 1024
    3. 2048
    4. 64

8. embed dim
    1. 256
    2. 512
    3. 1024

11. tokenizer
    1. sentencepiece with gold

12. dropout
    1. 0
    2. 0.1
    3. 0.2
    4. 0.3

13. attention dropout (*)
    1. 0
    2. 0.2
    3. 0.3

14. max expansion
    1. 50
    2. 800
