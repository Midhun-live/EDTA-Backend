from sqlalchemy import Column, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
import uuid

class AssessmentRecord(Base):
    __tablename__ = "assessments"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    user = relationship("User")
    share_id = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    share_token = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))

    patient = Column(JSON, nullable=False)
    input_data = Column(JSON, nullable=False)
    output_data = Column(JSON, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def patient_name(self):
        return self.patient.get("name", "Unknown") if self.patient else "Unknown"

    @property
    def patient_age(self):
        return self.patient.get("age", "Unknown") if self.patient else "Unknown"
