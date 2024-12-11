# 实时音频转写工具

这是一个使用 Amazon Transcribe Streaming 服务的实时音频转写工具。该工具可以将音频文件转换为文本，支持实时转写功能。

## 功能特点

- 支持实时音频转写
- 支持 PCM 格式音频文件
- 自动处理超过5分钟的音频文件
- 支持中文转写
- 输出 SRT 字幕格式

## 环境要求

- Python 3.10
- 有效的 AWS 凭证配置

## 快速开始

1. 克隆仓库后，直接运行启动脚本：

```bash
./run.sh
```

该脚本会自动：
- 创建 Python 3.10 虚拟环境（如果不存在）
- 安装所需依赖
- 运行转写程序

## 主要依赖

- aiofile：用于异步文件操作
- amazon-transcribe-streaming-sdk：AWS 转写服务 SDK

## 配置说明

在 `transcribe_audio.py` 中可以配置以下参数：

- SAMPLE_RATE：采样率（默认 16000）
- BYTES_PER_SAMPLE：每个采样的字节数（默认 2）
- CHANNEL_NUMS：声道数（默认 1）
- REGION：AWS 区域（默认 "us-west-2"）

## 注意事项

- 确保已正确配置 AWS 凭证
- 音频文件需要是 PCM 格式
- 虚拟环境（venv/）已被添加到 .gitignore
