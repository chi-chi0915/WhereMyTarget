from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models import Base


# PostgreSQL 연결 엔진
engine = create_engine(settings.database_url)

# DB 세션 생성기 (자동 커밋, 플러시 off) -> FastAPI는 SessionLocal()로 DB 활용
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base.metadata에 등록된 모든 테이블을 생성 -> 이미 있는 테이블은 생성 안함
def create_tables():
    Base.metadata.create_all(bind=engine)


def test_db_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return result.scalar()


def get_db():
    db = SessionLocal()
    try:
        # 요청하면 사용할 DB 세션을 전달
        # 종료 후 finally에서 세션을 닫음
        # yield는 return과 달리 값을 넘겨주고 함수 실행을 잠깐 멈춤
        yield db
    finally:
        db.close()