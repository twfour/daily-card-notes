# 每日一篇

一个卡片式每日记录网页，包含静态前端和小型 Python + SQLite 后端。

## 本地运行

```bash
python3 -B server.py
```

打开：

```text
http://127.0.0.1:8001/
```

## Render Free 部署

仓库包含 `render.yaml`，可在 Render 中使用 Blueprint 创建服务。

配置要点：

- 服务类型：Web Service
- Runtime：Python
- Plan：Free
- Start Command：`python3 -B server.py`
- Health Check Path：`/api/health`

注意：Render Free Web Service 没有持久磁盘。当前 SQLite 数据库文件可以在实例运行期间保存内容，但重新部署、休眠恢复或实例替换后不保证保留。要可靠长期保存，需要改用外部数据库，或使用支持持久磁盘的付费配置。
