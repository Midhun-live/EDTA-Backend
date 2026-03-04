import uuid
from sqlalchemy import text
from app.db.database import engine

with engine.connect() as conn:
    try:
        conn.execute(text('ALTER TABLE assessments ADD COLUMN share_token VARCHAR;'))
        conn.execute(text('CREATE UNIQUE INDEX ix_assessments_share_token ON assessments (share_token);'))
        conn.commit()
        print('Migration successful')
    except Exception as e:
        print(e)

