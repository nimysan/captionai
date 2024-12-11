#!/bin/bash

# Check if virtual environment exists, create if it doesn't
if [ ! -d "venv" ]; then
    python3.10 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python -m pip install amazon-transcribe # 手动安装本地版本
else
    source venv/bin/activate
fi

# Run the transcription script
python transcribe_audio.py
