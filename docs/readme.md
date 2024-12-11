# for it

## 测试资源说明
1. 原版-带噪音-中文-男声.mp4 , 是 央视 对于一个视频的真实讲解
2. match_by_polly.wav 是使用Amazon Polly生成的一段相对比较简单的解说 （语气非常平缓）

## 一定一定要注意

### media_sample_rate_hz一定要跟音频匹配， 才能出现好的效果。 
```python
# media_sample_rate_hz一定要跟音频匹配， 才能出现好的效果。 
stream = await client.start_stream_transcription(
    language_code="zh-CN",
    media_sample_rate_hz=44100,  # 将采样率设置为 44100 Hz
    media_encoding="pcm",
)

```

### 背景音的影响其实不是很大

https://www.lalal.ai/zh-hans/guides/how-to-remove-background-music/ 效果特别好 
去掉更好。

去噪相对来说比较简单 -----

## 
请求的url:
wss://transcribestreaming.eu-west-1.amazonaws.com:8443/stream-transcription-websocket?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIAVV2N3GNTTC5VJP2C%2F20241101%2Feu-west-1%2Ftranscribe%2Faws4_request&X-Amz-Date=20241101T064129Z&X-Amz-Expires=15&X-Amz-Security-Token=IQoJb3JpZ2luX2VjECcaCWV1LXdlc3QtMSJHMEUCIQCJU4TKwxxgPpFuoWciENFEXxU1dJJG%2BeutOPQSPZSdLgIgGD9ceX9g%2BPE4n4EDp503sHDhFfpsSuaAipY92%2FgfK%2BUq9QIIoP%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARABGgwzOTA0Njg0MTYzNTkiDJz6wd%2BKttr0r2j2KyrJAugTo2%2FP1TvqPNRCLd12vWFikj8Ue4kW0XW44w8HDdi6j%2BPJrPs7J3VFU0wC1CJBWj6uo384T0yL1G1a1RcEr1Focmn%2F0juDaFXuaiZmRjz9Jg5mlp4xwtd52BfNzes9Ph5hgBbrFwMXd29PSJ9e2HU59%2F2YaXaHjd2mGpaTWyBoOGVTZpGLV3cNae6zvFm6LFEHioCDAL9gm7H2J58PbbQlJxTej%2FaJGm%2FK9p0stcei%2B1CKHlp3wZA85CZgPQijh1s5MkB6axmbYs7%2FbM97ZUMZNp2lCK72xed63FKGv60mXaufP0vzwqXtzafUXdSHmK4TCeErRlHZARLrfifalvNjefmL5IewAjj026qGr5abWjo9JOR5Y61uVfVJPVq5E3NdL6GWQ6ATtYKC%2FwMqxAS8Sgce6%2BSY%2B44OXRPMTK2RPuJmYGK9isl6MNvskbkGOocCQX2pdtq3vyA%2FLJHGt7049bNt9OYGAqm8%2Fqobr1FZHacD3H9%2Bg4u5ziXABD23LW4cX1easU%2FnPYKtR8p7UM2k%2BrtdN%2BTssbsdYbNQzkfC%2FheoTrusFyNFGT7H23pLorsxQTcWOkt2QbtUtekUfJO4Rj%2B9GF3WLtCI4l03%2FZJ0oOkMqIjT2YIunlPhwZ8HuKykp%2BsJJmDAHwi3cqBGmUjquL8QRUg9pQxv1QQugZLpHcjcUCi2p9sUbb8nb0L0FLy0kNGb4VKKrePI4S03FXGtq7Z%2FOdxq70uvoW190VPxgAsVxNmxWvlmmWg1sTQubpSAxcqq8S6FEZ8u6iTbV03z9ghhgoZbVJw%3D&X-Amz-Signature=307083c6cf34234e0a8dab15ceb76b95422789dcdc6426b867ee70b959ce0e8a&X-Amz-SignedHeaders=host&language-code=en-US&media-encoding=pcm&sample-rate=16000

![img.png](img.png)

不同的 input 和 output

## 集成代码

[代码和使用方式](https://github.com/awslabs/amazon-transcribe-streaming-sdk/blob/7eae6ca02aad56ce5865910cb9715ac77bc2adeb/README.md)


## 例子语音

阿拉伯语音例子： https://www.kaggle.com/code/mpwolke/arabic-speech-to-text-wav



ffmpeg -i match_test.wav -f lavfi -i color=c=black:s=1280x720 -c:v libx264 -crf 23 -preset veryfast -c:a copy -shortest output.mp4

## 关键步骤 - 分离背景音乐
> https://github.com/deezer/spleeter
spleeter -> https://blog.csdn.net/zengraoli/article/details/104581306

spleeter separate -p spleeter:2stems -o output test.wav
ffmpeg -i test.wav -acodec copy -map 0:0 -vn vocals.mp3
ffmpeg -i test.wav -af "voiceremove=sp=0.8" -ar 44100 output_voice.wav

ffmpeg -i test.wav -ac 1 -ar 16000 -f wav - | sox --multi-threaded -t wav - -t wav output_voice.wav noisered sox_voice 0.8 0.6 

### 一个非常好的在线网站 --- 
> https://www.lalal.ai/zh-hans/guides/how-to-remove-background-music/  
效果特别好 ---


## 配置和设定

### match_test.wav
 Stream #0:0: Audio: pcm_s16le ([1][0][0][0] / 0x0001), 22050 Hz, 1 channels, s16, 352 kb/s

### vocak.wav
 Stream #0:0: Audio: pcm_s16le ([1][0][0][0] / 0x0001), 44100 Hz, 2 channels, s16, 1411 kb/s



### 