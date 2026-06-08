#!/usr/bin/env python3
import json
import os
import sqlite3
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "daily_notes.sqlite3"
PORT = int(os.environ.get("PORT", "8001"))

BUILT_IN_ENTRIES = [
    {
        "id": "built-in-2026-06-06-chocolate",
        "title": "巧克力",
        "content": "巧克力是一个人的爱情\n也可以是大众的爱情\n当我们摘掉别人的意义\n便有了自己的意义\n\n谢晓萍 | 巧克力",
        "category": "诗句",
        "mood": "微澜",
        "type": "短诗句",
        "share": "分享这句「巧克力是一个人的爱情，也可以是大众的爱情。当我们摘掉别人的意义，便有了自己的意义」：它把巧克力从礼物、节日和他人的解释里轻轻取回，变成一个人重新命名生活的权利。爱情可以属于众人，也可以只属于此刻的自己。",
        "dateKey": "2026-06-06",
        "dateLabel": "2026年6月6日星期六",
        "createdAt": 1780713600000,
    },
    {
        "id": "built-in-2026-06-07-baba-yaga",
        "title": "稍停片刻",
        "content": "我们在这里稍停片刻，人生是一片原野，其间有风穿过，故事时而狭窄，时而辽阔。\n\n杜布拉夫卡·乌格雷西奇 | 芭芭雅嘎下了个蛋",
        "category": "读书",
        "mood": "安静",
        "type": "短诗句",
        "share": "分享这句「我们在这里稍停片刻，人生是一片原野，其间有风穿过，故事时而狭窄，时而辽阔」：它像把人从赶路里轻轻拦下，让我们看见故事并不总是直线。狭窄时有风，辽阔时也有风，停一停，才知道自己正站在怎样的原野里。",
        "dateKey": "2026-06-07",
        "dateLabel": "2026年6月7日星期日",
        "createdAt": 1780800000000,
    },
    {
        "id": "built-in-2026-06-08-brautigan-metaphors",
        "title": "布劳提根的比喻",
        "content": "布劳提根简直是古希腊掌管比喻的神：\n\n■ 夏天，它像石头一样硬。\n\n■ 他的眼睛像一块带伤的地毯，湿漉漉的。\n\n■ 我尽我所能地去安慰他，像是台奇怪的吸尘器。\n\n■ 我像矮小的堂吉诃德，脚下留下一连串的大冒险。\n\n■ 灰色的木台阶像一只老母猫，要上三层楼梯才能到她门前。\n\n■ 我走上通向阁楼的楼梯。我小心翼翼地走着，好像抚摸着一只正在哺乳的老灰猫。\n\n■ 她打开钱包，钱包就像一片秋天的小田野。在一棵老苹果树倒下的树枝旁，她找到了她的钥匙。\n\n■ 我看了眼桌子。一罐速溶咖啡，空杯子和勺子像参加葬礼一样，依次排开。这些是你泡一杯咖啡需要的东西。\n\n■ 像大多数加州人一样，我来自其他地方，为了服务加州而聚集于此，就像一朵吃金属的花收集阳光和雨水，然后向高速公路展示自己的花瓣，再让汽车驶入。\n\n■ 这好像是纯粹的能量，就是那种吃金属的花的影子，把我们从别样的生命中召唤出来，都来塑造加利福尼亚，直到最后都变成像停车计时器形状的泰姬陵。",
        "category": "读书",
        "mood": "欢喜",
        "type": "文章",
        "share": "",
        "dateKey": "2026-06-08",
        "dateLabel": "2026年6月8日星期一",
        "createdAt": 1780886400000,
    },
]


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS entries (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT NOT NULL,
                mood TEXT NOT NULL,
                type TEXT NOT NULL,
                share TEXT NOT NULL DEFAULT '',
                date_key TEXT NOT NULL,
                date_label TEXT NOT NULL,
                created_at INTEGER NOT NULL
            )
            """
        )
        conn.executemany(
            """
            INSERT OR IGNORE INTO entries (
                id, title, content, category, mood, type, share,
                date_key, date_label, created_at
            ) VALUES (
                :id, :title, :content, :category, :mood, :type, :share,
                :dateKey, :dateLabel, :createdAt
            )
            """,
            BUILT_IN_ENTRIES,
        )


def row_to_entry(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "content": row["content"],
        "category": row["category"],
        "mood": row["mood"],
        "type": row["type"],
        "share": row["share"],
        "dateKey": row["date_key"],
        "dateLabel": row["date_label"],
        "createdAt": row["created_at"],
    }


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            self.respond_json({"ok": True})
            return
        if parsed.path == "/api/entries":
            with connect() as conn:
                rows = conn.execute(
                    "SELECT * FROM entries ORDER BY created_at DESC"
                ).fetchall()
            self.respond_json([row_to_entry(row) for row in rows])
            return
        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/entries":
            self.send_error(404)
            return

        entry = self.read_json()
        required = [
            "id",
            "title",
            "content",
            "category",
            "mood",
            "type",
            "dateKey",
            "dateLabel",
            "createdAt",
        ]
        if not entry or any(key not in entry for key in required):
            self.respond_json({"error": "missing required entry fields"}, status=400)
            return

        entry["share"] = entry.get("share", "")
        with connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO entries (
                    id, title, content, category, mood, type, share,
                    date_key, date_label, created_at
                ) VALUES (
                    :id, :title, :content, :category, :mood, :type, :share,
                    :dateKey, :dateLabel, :createdAt
                )
                """,
                entry,
            )
        self.respond_json(entry, status=201)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        prefix = "/api/entries/"
        if not parsed.path.startswith(prefix):
            self.send_error(404)
            return

        entry_id = parsed.path[len(prefix) :]
        with connect() as conn:
            cursor = conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        if cursor.rowcount == 0:
            self.respond_json({"error": "entry not found"}, status=404)
            return
        self.respond_json({"ok": True})

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return None
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except json.JSONDecodeError:
            return None

    def respond_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    init_db()
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Serving http://127.0.0.1:{PORT}")
    print(f"Database {DB_PATH}")
    server.serve_forever()
