from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.document import DocumentDetailResponse, DocumentListItem
from app.services.document_service import DocumentService

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)

# 서비스 객체 생성
document_service = DocumentService()


# 문서 업로드
@router.post("")
def create_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        return document_service.create_document(file=file, db=db)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"문서 업로드 중 오류가 발생했습니다. error={str(e)}",
        )


# 문서 목록 조회
@router.get("", response_model=list[DocumentListItem])
def find_documents(db: Session = Depends(get_db)):
    try:
        return document_service.find_documents(db=db)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"문서 목록 조회 중 오류가 발생했습니다. error={str(e)}",
        )


# 문서 상세 조회
@router.get("/{document_id}", response_model=DocumentDetailResponse)
def find_document_detail(
    document_id: int,
    db: Session = Depends(get_db),
):
    try:
        return document_service.find_document_detail(
            db=db,
            document_id=document_id,
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"문서 상세 조회 중 오류가 발생했습니다. error={str(e)}",
        )
    
@router.get("/{document_id}/file")
def get_document_file(
    document_id: int,
    db: Session = Depends(get_db),
):
    try:
        file_path, original_filename = document_service.get_document_file(
            db=db,
            document_id=document_id,
        )

        return FileResponse(
            path=file_path,
            media_type="application/pdf",
            filename=original_filename,
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"문서 파일 조회 중 오류가 발생했습니다. error={str(e)}",
        )
    
# 문서 삭제
@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    try:
        return document_service.delete_document(
            db=db,
            document_id=document_id,
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"문서 삭제 중 오류가 발생했습니다. error={str(e)}",
        )