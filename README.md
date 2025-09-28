# AI多角色语音聊天系统

本项目支持多角色对话、语音输入（ASR）、文本处理（LLM）、语音朗读（TTS），支持微调后的 ChatGLM3-6B 模型，前后端可分离运行。

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

系统需预先安装：
- `ffmpeg`（音频处理）
- `edge-tts`（更高质量朗读）

### 运行服务

```bash
python app.py
```

浏览器访问：http://localhost:5000

## 项目结构

```
├── app.py              # 后端主入口
├── index.html          # 静态前端页面
├── asr_service.py      # ASR 模块
├── tts_service.py      # TTS 模块
├── text_process.py     # 文本处理逻辑（可替换）
├── requirements.txt    # 项目依赖
├── /uploads            # 上传音频
└── /tts_audio          # 输出音频
```

## 模型说明：ChatGLM3-6B 微调

使用模型：`THUDM/chatglm3-6b`

每次运行微调脚本后，会生成对应角色的 LoRA 参数，保存在：

```
model/<角色名>/
```

微调训练及部署详见：

[Kaggle Notebook 训练地址](https://www.kaggle.com/code/firstsnowafterwind/aichat-finetune)

## 替换文本处理逻辑

在 `text_process.py` 中修改 `process_text(raw_text)` 函数，返回格式必须为：

```python
{
  "processed_text": "角色回复内容",
  "tts_options": {
    "voice": "zh-CN-XiaoxiaoNeural",  # 角色语音
    "rate": 1.0                       # 语速
  }
}
```

你可以根据角色切换不同的 voice ID。

## 多角色语音配置（edge-tts 语音）

示例 voice 配置：
- `zh-CN-XiaoxiaoNeural`：中文女声
- `zh-CN-YunxiNeural`：中文男声
- `en-US-JennyNeural`：英文女声

更多 voice 见：
```bash
edge-tts --list-voices | grep zh-CN
```

## requirements.txt 内容

```txt
Flask==2.3.2
pyttsx3==2.90
edge-tts==6.1.5
pydub==0.25.1
librosa==0.10.1
soundfile==0.12.1
openai-whisper==20231117
torch>=1.12
numpy>=1.21
uuid
```

---
