"""代码审查示例"""

import asyncio

from flowpilot import DevFlow


CODE_SNIPPET = """
import hashlib
import sqlite3

def create_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')"
    cursor.execute(query)
    conn.commit()
    conn.close()

def authenticate(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = f"SELECT password FROM users WHERE username = '{username}'"
    result = cursor.fetchone()
    conn.close()
    if result and result[0] == password:
        return True
    return False
"""


async def main():
    flow = DevFlow()

    try:
        result = await flow.run(
            f"请审查以下代码的安全性和质量：\n{CODE_SNIPPET}",
            mode="review",
        )
        print(result.review)
    finally:
        await flow.close()


if __name__ == "__main__":
    asyncio.run(main())
