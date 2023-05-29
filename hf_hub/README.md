---
license:
- cc-by-sa-3.0
- gfdl
dataset_info:
- config_name: corpus-jawiki-20230403
  features:
  - name: text
    dtype: string
  splits:
  - name: train
    num_bytes: 3569619848
    num_examples: 24387500
  download_size: 1297833377
  dataset_size: 3569619848
- config_name: corpus-jawiki-20230403-cirrus
  features:
  - name: text
    dtype: string
  splits:
  - name: train
    num_bytes: 4779055224
    num_examples: 28018607
  download_size: 1730081783
  dataset_size: 4779055224
- config_name: corpus-jawiki-20230403-filtered-large
  features:
  - name: text
    dtype: string
  splits:
  - name: train
    num_bytes: 3027074884
    num_examples: 20133720
  download_size: 1092808039
  dataset_size: 3027074884
- config_name: paragraphs-jawiki-20230403
  features:
  - name: id
    dtype: string
  - name: pageid
    dtype: int64
  - name: revid
    dtype: int64
  - name: paragraph_index
    dtype: int64
  - name: title
    dtype: string
  - name: section
    dtype: string
  - name: text
    dtype: string
  - name: html_tag
    dtype: string
  splits:
  - name: train
    num_bytes: 4417130987
    num_examples: 9668476
  download_size: 1489512230
  dataset_size: 4417130987
- config_name: passages-c300-jawiki-20230403
  features:
  - name: id
    dtype: int64
  - name: pageid
    dtype: int64
  - name: revid
    dtype: int64
  - name: title
    dtype: string
  - name: section
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: train
    num_bytes: 3939431360
    num_examples: 6639833
  download_size: 1402596784
  dataset_size: 3939431360
- config_name: passages-c400-jawiki-20230403
  features:
  - name: id
    dtype: int64
  - name: pageid
    dtype: int64
  - name: revid
    dtype: int64
  - name: title
    dtype: string
  - name: section
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: train
    num_bytes: 3868482519
    num_examples: 5555583
  download_size: 1393661115
  dataset_size: 3868482519
- config_name: passages-para-jawiki-20230403
  features:
  - name: id
    dtype: int64
  - name: pageid
    dtype: int64
  - name: revid
    dtype: int64
  - name: title
    dtype: string
  - name: section
    dtype: string
  - name: text
    dtype: string
  splits:
  - name: train
    num_bytes: 3751418134
    num_examples: 9397066
  download_size: 1296071247
  dataset_size: 3751418134
language:
- ja
size_categories:
- 10M<n<100M
---

# Wikipedia-Utils: Preprocessed Wikipedia Texts for NLP

Preprocessed Wikipedia texts generated with the scripts in [singletongue/wikipedia-utils](https://github.com/singletongue/wikipedia-utils) repo.

For detailed information on how the texts are processed, please refer to the repo.
