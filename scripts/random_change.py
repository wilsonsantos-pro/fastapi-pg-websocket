import random
import time

from sqlalchemy import insert, select, update

from fastapi_pg_websocket.database import db_session_ctx
from fastapi_pg_websocket.orm import User


def main():
    with db_session_ctx() as db:
        users = db.scalars(select(User)).all()
        if not users:
            db.execute(
                insert(User).values(
                    [
                        {"username": "alice", "email": "alice@example.com"},
                        {"username": "bob", "email": "bob@example.com"},
                        {"username": "charlie", "email": "charlie@example.com"},
                    ]
                )
            )
            db.commit()
            users = db.scalars(select(User)).all()

        while True:
            user = random.choice(users)
            status = random.randint(1, 1000)
            db.execute(update(User).where(User.id == user.id).values(status=status))

            db.commit()
            time.sleep(3)


if __name__ == "__main__":
    main()
