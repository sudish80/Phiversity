from sqlalchemy.orm import Session
from scripts.server.logger import logger

class BaseService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logger
