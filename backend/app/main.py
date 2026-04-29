from fastapi import FastAPI
from app.database import test_db_connection, create_tables

# API 객체
app = FastAPI(title="WhereMyTarget API")


#@는 데코레이터로 부르고 API를 주소 정의함
#해당 주소로 접근하면 함수를 실행함
@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/db-test")
def db_test():
    result = test_db_connection()
    return {"db": "connected", "result": result}

@app.post("/create-tables")
def create_tables_api():
    create_tables()
    return {"message": "tables created"}