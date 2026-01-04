from sqlalchemy import Column, String, JSON, DateTime
from app.db.base import Base
from datetime import datetime

class AssessmentRecord(Base):
    __tablename__ = "assessments"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)

    patient = Column(JSON, nullable=False)
    input_data = Column(JSON, nullable=False)
    output_data = Column(JSON, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
