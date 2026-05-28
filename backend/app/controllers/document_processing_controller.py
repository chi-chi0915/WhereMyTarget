from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.document_processing_service import DocumentProcessingService
from app.services.document_embedding_service import DocumentEmbeddingService

router = APIRouter(
    prefix="/documents",
    tags=["document-processing"],
)

# 서비스 객체 생성
document_processing_service = DocumentProcessingService()
document_embedding_service = DocumentEmbeddingService()

# 문서 파싱
@router.post("/{document_id}/parse")
def parse_document(document_id: int, db: Session = Depends(get_db)):
    try:
        return document_processing_service.parse_document(
            db=db,
            document_id=document_id,
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문서 파싱 중 오류가 발생했습니다. error={str(e)}")

# 문서 임베딩    
@router.post("/{document_id}/embed")
def embed_document(document_id: int, db: Session = Depends(get_db)):
    try:
        return document_embedding_service.embed_document(
            db=db,
            document_id=document_id,
        )

    except ValueError as e:
        message = str(e)

        if "문서를 찾을 수 없습니다" in message:
            raise HTTPException(status_code=404, detail=message)

        raise HTTPException(status_code=400, detail=message)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문서 embedding 중 오류가 발생했습니다. error={str(e)}")