# Dash流外接字幕

是的,DASH流可以支持外挂字幕。

在DASH中,字幕通常被当作一个独立的"补充轨"(Supplemental Track)来处理。字幕数据被存储在独立的XML文件中,使用TTML或WebVTT格式。

在DASH的媒体呈现描述(MPD)文件中,会有一个EssentialProperty节点来标识字幕轨,包括字幕的语言、角色等元数据信息。播放器根据MPD文件加载字幕轨,并将其渲染到视频播放区域。

因此,只需要将字幕文件放在与视频文件同级的路径下,并正确配置MPD文件,DASH播放器就可以自动加载并显示外挂字幕了。这种方式使得字幕可以作为一个可选组件,用户可以根据需求开启或关闭字幕。

总的来说,DASH对外挂字幕的支持还是比较好的,并遵循了行业标准,这样可以最大限度地增强内容的可访问性。

## 测试资源

https://ottverse.com/free-mpeg-dash-mpd-manifest-example-test-urls/

## 字幕例子

https://reference.dashif.org/dash.js/nightly/samples/captioning/caption_vtt.html


### 格式实现

```xml
<AdaptationSet mimeType="text/vtt" lang="en"> 
    <Representation id="caption_en" bandwidth="256">
        <BaseURL>https://dash.akamaized.net/akamai/test/caption_test/ElephantsDream/ElephantsDream_en.vtt</BaseURL> 
    </Representation>
</AdaptationSet>

```
