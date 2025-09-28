def process_text(raw_text: str, role: str):
    # 最后替换成notebook中的函数调用
    reply_map = {
        "c1": "我们需要冷静分析这个情况。",
        "c2": "哇哈哈，这听起来太有趣了！",
        "c3": "我理解你的感受，你辛苦了。",
        "c4": "This is not nonsense, move faster!",
        "c5": "在这个问题上，我们可以这样思考……",
        "c6": "人生如诗，唯有静心方得始终。"
    }
    response = reply_map.get(role, "默认角色回复")
    tts_options = {
        "rate": "+0%",  # 语速可以根据角色不同调整
    }
    return response, tts_options
