from sqlalchemy import column, Integer, String, Boolean
from sqlalchemy.engine.result import ResultMetaData
from sqlalchemy.sql.operators import collate
from sqlalchemy.sql.schema import Column
from database import Base

class notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    message = Column(String)
    timestamp = Column(Integer) 
    is_read = Column(Boolean)
    is_seen = Column(Boolean)
    link = Column(String)
