# IMPORTANT: RUN THIS FILE FROM GIT ROOT ANd SEND THIS FILE AS PARAMETER!

# Select base image
FROM pytorch/pytorch
# FROM pytorch/pytorch:0.4.1-cuda9-cudnn7-runtime

WORKDIR /workspace

# Identify the maintainer of the image
LABEL maintainer="yoshio@axeleratum.com"

# Run necessary commands like if you are in bash
RUN mkdir /workspace/model
RUN mkdir /workspace/model/config
RUN mkdir /workspace/service
RUN mkdir /workspace/sentiments_logs

# Copy files from local to docker image
COPY ["./Models/BERT PyTorch/tokenization.py", "model/tokenization.py"]
COPY ["./Models/BERT PyTorch/modeling.py", "model/modeling.py"]
COPY ["./Models/BERT PyTorch/multi_cased_L-12_H-768_A-12/bert_config.json", "model/config/bert_config.json"]
COPY ["./Models/BERT PyTorch/multi_cased_L-12_H-768_A-12/vocab.txt", "model/config/vocab.txt"]
COPY ["./Models/BERT Sentiments/CT NoPN/model_comm_3_chkpt_4.bin", "model/config/sentiments_chkpt.bin"]

COPY ["./Models/BERT Sentiments/bert_sentiments_service.py", "service/bert_sentiments_service.py"]
COPY ["./Models/BERT Sentiments/bert_sentiments_service_processor.py", "service/bert_sentiments_service_processor.py"]
COPY ["./Models/BERT Sentiments/bert_sentiments_service_utils.py", "service/bert_sentiments_service_utils.py"]

# Install necessary packages
RUN pip install spacy
RUN python -m spacy download es_core_news_md
RUN pip install flask
RUN pip install flask_restful

# Expose port where the image will be serving ORIGIN TARGET
EXPOSE 5000 8080

# Define environment variable
ENV PYTHONPATH "${PYTHONPATH}:model"

# Set the command at starting point
CMD ["python", "service/bert_sentiments_service.py", "--task_name", "sentihood_NLI_M", "--vocab_file", "\"model/config/vocab.txt\"", "--bert_config_file", "\"model/config/bert_config.json\"", "--init_checkpoint", "\"model/config/sentiments_chkpt.bin\"", "--max_seq_length", "256", "--local_rank", "-1", "--batch_size", "8", "--seed", "42", "--host", "\"0.0.0.0\"", "--port", "5000", "--log_file", "sentiments_logs/sentiments.log" ]
