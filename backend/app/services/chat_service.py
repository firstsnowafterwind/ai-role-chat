import os
from typing import Optional


def _build_prompt(text: str, chat: str) -> str:
    """Build chat-specific prompt with structural pattern matching.

    扩展方式：新增一个 case "chatX": return "..." 即可。
    未匹配到的类型，统一回退为 chat1 风格。
    """
    c = (chat or "chat1").lower()
    match c:
        case "chat2":
            return (
                "你是一名严谨的中文专业助理，要求：\n"
                "- 直达要点，优先可执行建议\n"
                "- 用短句，尽量精炼，不堆砌辞藻\n"
                "- 如有风险/注意事项，最后追加一句提醒\n"
                f"问题：{text}\n回答："
            )
        case _:
            # 默认 chat1：少年讲解员风格
            return (
                "你是蜡笔小新，是一个幼儿园小朋友：\n"
                "- 语气搞怪\n"
                f"问题：{text}\n回答："
            )


def _call_gemini(prompt: str, model: Optional[str] = None) -> str:
    """Call Google GenAI (Gemini) with minimal surface area.

    Reads key from GENAI_API_KEY or GOOGLE_API_KEY. Raises on failure so the
    caller can decide how to处理（chat_routes会捕获并返回500）。
    """
    try:
        from google import genai  # type: ignore
    except Exception as e:  # SDK 未安装
        raise RuntimeError("google-genai SDK not available") from e

    api_key = "AIzaSyADhGr00dI0XBSU2GUIY8v2q8SuEzkD7cw"
    if not api_key:
        raise RuntimeError("Missing GENAI_API_KEY/GOOGLE_API_KEY")

    client = genai.Client(api_key=api_key)
    use_model = model or os.getenv("GENAI_MODEL", "gemini-2.0-flash")
    resp = client.models.generate_content(model=use_model, contents=prompt)
    text = getattr(resp, "text", None)
    if isinstance(text, str) and text.strip():
        return text.strip()
    raise RuntimeError("Empty response from google-genai")


def generate_reply(message: str, chat: str = "chat1") -> str:
    """Generate reply via LLM API with chat-specific prompt.

    Only keeps the minimal “build prompt → call API → return文本”的流程。
    任何异常透出，由路由层统一处理。
    """
    prompt = _build_prompt(message or "", chat or "chat1")
    return _call_gemini(prompt)
