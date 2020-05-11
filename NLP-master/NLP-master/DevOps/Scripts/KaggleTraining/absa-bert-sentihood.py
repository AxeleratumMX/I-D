import os

convert_command = '''
python ../input/absabert/convert_tf_checkpoint_to_pytorch.py \
--tf_checkpoint_path ../input/multi-cased-l12-h768-a12-110319/bert_model.ckpt \
--bert_config_file ../input/multi-cased-l12-h768-a12-110319/bert_config.json \
--pytorch_dump_path pytorch_model.bin
'''

train_command = '''
python ../input/absabert/run_classifier_TABSA.py \
--task_name sentihood_NLI_B \
--data_dir ../input/absabertsentihood \
--vocab_file ../input/multi-cased-l12-h768-a12-110319/vocab.txt \
--bert_config_file ../input/multi-cased-l12-h768-a12-110319/bert_config.json \
--init_checkpoint pytorch_model.bin \
--eval_test \
--do_lower_case \
--max_seq_length 512 \
--train_batch_size 6 \
--learning_rate 2e-5 \
--num_train_epochs 3.0 \
--output_dir results \
--seed 42
'''

os.system(convert_command)
os.system(train_command)