import uuid
from sqlalchemy import text
from app.db.database import engine

with engine.connect() as conn:
    try:
        conn.execute(text('ALTER TABLE assessments ADD COLUMN share_id VARCHAR;'))
        conn.execute(text('CREATE UNIQUE INDEX ix_assessments_share_id ON assessments (share_id);'))
        conn.commit()
        print('Migration successful')
    except Exception as e:
        print(e)

