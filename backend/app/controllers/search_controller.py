from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.search import SearchRequest, SearchResponse
from app.services.search_service import SearchService


router = APIRouter(
    prefix="/search",
    tags=["search"],
)

# 서비스 객체 생성
search_service = SearchService()


# 전체 문서 chunk 검색
@router.post("", response_model=SearchResponse)
def search_chunks(
    request: SearchRequest,
    db: Session = Depends(get_db),
):
    try:
        return search_service.search(
            db=db,
            query=request.query,
            document_id=None,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"검색 중 오류가 발생했습니다. error={str(e)}",
        )


# 단건 문서 chunk 검색
@router.post("/documents/{document_id}", response_model=SearchResponse)
def search_document_chunks(
    document_id: int,
    request: SearchRequest,
    db: Session = Depends(get_db),
):
    try:
        return search_service.search(
            db=db,
            query=request.query,
            document_id=document_id,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"문서 검색 중 오류가 발생했습니다. error={str(e)}",
        )