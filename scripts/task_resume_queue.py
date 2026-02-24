#!/usr/bin/env python3
import argparse
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
QUEUE_PATH = ROOT / "memory" / "task-resume-queue.json"
MAX_ITEMS = 30


def load_queue():
    if not QUEUE_PATH.exists():
        return []
    try:
        return json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_queue(q):
    QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    QUEUE_PATH.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")


def norm(s):
    return " ".join((s or "").strip().lower().split())


def add_item(title, context, acceptance, source, session):
    now = int(time.time())
    q = load_queue()
    tnorm = norm(title)
    cnorm = norm(context)

    for item in q:
        if norm(item.get("title")) == tnorm and norm(item.get("context")) == cnorm:
            item["updated_at"] = now
            if source:
                item["source"] = source
            if session:
                item["session"] = session
            save_queue(q)
            print(json.dumps({"status": "updated", "item": item}, ensure_ascii=False))
            return

    item = {
        "id": f"tr_{now}_{len(q)+1}",
        "title": title,
        "context": context,
        "acceptance": acceptance,
        "source": source,
        "session": session,
        "created_at": now,
        "updated_at": now,
    }
    q.append(item)

    if len(q) > MAX_ITEMS:
        q = q[-MAX_ITEMS:]

    save_queue(q)
    print(json.dumps({"status": "added", "item": item}, ensure_ascii=False))


def pop_item():
    q = load_queue()
    if not q:
        print(json.dumps({"status": "empty"}, ensure_ascii=False))
        return
    item = q.pop(0)
    save_queue(q)
    print(json.dumps({"status": "popped", "item": item}, ensure_ascii=False))


def list_items():
    q = load_queue()
    print(json.dumps({"status": "ok", "count": len(q), "items": q}, ensure_ascii=False))


def status_items():
    q = load_queue()
    by_source = {}
    by_session = {}
    for item in q:
        src = item.get("source") or "unknown"
        ses = item.get("session") or "unknown"
        by_source[src] = by_source.get(src, 0) + 1
        by_session[ses] = by_session.get(ses, 0) + 1
    print(json.dumps({
        "status": "ok",
        "count": len(q),
        "by_source": by_source,
        "by_session": by_session,
    }, ensure_ascii=False))


def clear_items():
    save_queue([])
    print(json.dumps({"status": "cleared"}, ensure_ascii=False))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add")
    p_add.add_argument("--title", required=True)
    p_add.add_argument("--context", required=True)
    p_add.add_argument("--acceptance", default="")
    p_add.add_argument("--source", default="")
    p_add.add_argument("--session", default="")

    sub.add_parser("pop")
    sub.add_parser("list")
    sub.add_parser("status")
    sub.add_parser("clear")

    args = p.parse_args()

    if args.cmd == "add":
        add_item(args.title, args.context, args.acceptance, args.source, args.session)
    elif args.cmd == "pop":
        pop_item()
    elif args.cmd == "list":
        list_items()
    elif args.cmd == "status":
        status_items()
    elif args.cmd == "clear":
        clear_items()
