from app.database import engine
from sqlalchemy import text

with engine.connect() as connection:
    result = connection.execute(text("SELECT COUNT(*) FROM customer"))
    count = result.scalar()
    print(f"Customer count: {count}")
