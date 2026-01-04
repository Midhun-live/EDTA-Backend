from app.db.database import engine
from app.db.base import Base

from app.models.users import User
from app.models.assessment_record import AssessmentRecord

Base.metadata.create_all(bind=engine)
