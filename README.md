# Flask 前后端示例（模块化解耦）

一个最小但结构清晰的 Flask 前后端聊天示例：前端提供输入框/输出区/发送按钮；后端提供 `/api/chat` 接口，当前为 echo 实现（原样返回输入）。

## 目录结构

```
├── backend/
│   ├── app/
│   │   ├── __init__.py          # 创建 Flask 应用、注册蓝图、静态资源映射
│   │   ├── config.py            # 环境变量配置（DEBUG、SECRET_KEY、DB_URI）
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── chat_routes.py   # 聊天接口 /api/chat
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── chat_service.py  # 业务逻辑（当前回声）
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   └── logger.py        # 简易日志封装
│   │   └── main.py              # 入口（create_app + app.run）
│   └── wsgi.py                  # 生产环境入口（Gunicorn/Uwsgi 等）
│
├── frontend/
│   ├── index.html               # 页面（输入框、输出区、发送按钮）
│   └── static/
│       ├── css/style.css        # 样式
│       └── js/app.js            # 前端逻辑（fetch /api/chat）
│
├── requirements.txt             # 依赖
├── run.py                       # 本地运行入口
├── .env                         # 环境变量示例
└── README.md
```

## 快速开始

- Python 3.10+
- 建议创建虚拟环境并安装依赖：

```
pip install -r requirements.txt
```

- 启动：

```
python run.py
```

- 打开浏览器访问：`http://127.0.0.1:5000/`

前端资源由后端直接映射（`/` 与 `/static/*`），避免本地开发时跨域/CORS 复杂度。

## 接口说明

- `POST /api/chat`
  - Body(JSON): `{ "message": "你好" }`
  - Response(JSON): `{ "reply": "你好" }`  // 当前为 echo
  - 错误: `{ "error": "message is required" }` → 400

## 下一步可拓展

- 在 `backend/app/services/chat_service.py` 中接入真实模型或代理链路。
- 增加会话上下文、数据持久化（DB_URI）。
- 增加鉴权、限流、日志分级、单元测试。

