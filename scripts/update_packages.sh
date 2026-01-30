#!/bin/bash
LOG_FILE="/home/ubuntu/llm_token_counter/logs/update.log"
VENV_PATH="/home/ubuntu/llm_token_counter/venv"

mkdir -p /home/ubuntu/llm_token_counter/logs

echo "========================================" >> $LOG_FILE
echo "Update started: $(date)" >> $LOG_FILE

source $VENV_PATH/bin/activate
pip install --upgrade transformers tiktoken anthropic google-genai huggingface-hub >> $LOG_FILE 2>&1

echo "Installed versions:" >> $LOG_FILE
pip show transformers tiktoken | grep -E "^(Name|Version)" >> $LOG_FILE

sudo systemctl restart tokenizer >> $LOG_FILE 2>&1

echo "Update completed: $(date)" >> $LOG_FILE
echo "========================================" >> $LOG_FILE
