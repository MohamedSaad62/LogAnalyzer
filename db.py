from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, Text

DATABASE_URL = "postgresql+asyncpg://user:userpassword@localhost/userdb"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class LogRecord(Base):
    __tablename__ = "log_records"
    id = Column(Integer, primary_key=True, index=True)
    log_text = Column(Text)
    reply = Column(Text)

async def push_to_db(log_text: str, reply: str):
    async with async_session() as session:
        record = LogRecord(log_text=log_text, reply=reply)
        session.add(record)
        await session.commit()
