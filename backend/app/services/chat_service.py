def generate_reply(message: str, chat: str = "chat1") -> str:
    """
    简单业务逻辑：
    - chat1: 原样返回
    - chat2: 将字符串反转返回
    其它: 默认按 chat1 处理
    """
    if (chat or "").lower() == "chat2":
        return message[::-1]
    return message
