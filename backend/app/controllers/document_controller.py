from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.document_service import DocumentService

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)

# 서비스 객체 생성
document_service = DocumentService()


@router.post("")
def create_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        return document_service.create_document(file=file, db=db)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        raise HTTPException(status_code=500, detail="문서 업로드 중 오류가 발생했습니다.")