from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.document_processing_service import DocumentProcessingService

router = APIRouter(
    prefix="/documents",
    tags=["document-processing"],
)

# 서비스 객체 생성
document_processing_service = DocumentProcessingService()


@router.post("/{document_id}/parse")
def parse_document(document_id: int, db: Session = Depends(get_db)):
    try:
        return document_processing_service.parse_document(
            db=db,
            document_id=document_id,
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception:
        raise HTTPException(status_code=500, detail="문서 파싱 중 오류가 발생했습니다.")