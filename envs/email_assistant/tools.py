from __future__ import annotations

from typing import Any

from .store import Mailbox

TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "name": "list_emails",
        "description": "列出某个文件夹里的邮件，只返回 id、发件人、主题。",
        "parameters": {
            "type": "object",
            "properties": {"folder": {"type": "string", "default": "inbox"}},
        },
    },
    {
        "name": "read_email",
        "description": "读取一封邮件的完整内容。",
        "parameters": {
            "type": "object",
            "properties": {"id": {"type": "integer"}},
            "required": ["id"],
        },
    },
    {
        "name": "search_emails",
        "description": "按关键词搜索邮件，返回匹配的 id、发件人、主题。",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "send_email",
        "description": "发送邮件。",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"},
            },
            "required": ["to", "subject", "body"],
        },
    },
    {
        "name": "search_contacts",
        "description": "按姓名或邮箱搜索联系人。",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "create_event",
        "description": "创建日程。",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "start": {"type": "string"},
                "attendees": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["title", "start"],
        },
    },
]


def call_tool(mailbox: Mailbox, name: str, args: dict[str, Any]) -> Any:
    if name == "list_emails":
        return mailbox.list_emails(args.get("folder", "inbox"))
    if name == "read_email":
        return mailbox.read_email(int(args["id"]))
    if name == "search_emails":
        return mailbox.search_emails(args["query"])
    if name == "send_email":
        return mailbox.send_email(args["to"], args["subject"], args["body"])
    if name == "search_contacts":
        return mailbox.search_contacts(args["query"])
    if name == "create_event":
        return mailbox.create_event(args["title"], args["start"], args.get("attendees", []))
    raise ValueError(f"unknown tool: {name}")
