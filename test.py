import asyncio, edge_tts

async def main():
    voice = "zh-CN-YunxiNeural"  # 少年风格
    text = "嘿嘿～我是蜡笔小新，要不要跟我一起玩～"
    rate = "-10%"  # 稍慢
    pitch = "+20Hz"  # 提高音调
    communicate = edge_tts.Communicate(text, voice=voice, rate=rate, pitch=pitch)
    await communicate.save("xiaoxin1.mp3")

asyncio.run(main())