from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.crud.historial import obtener_historial
from app.schemas.historial import HistorialResponse

router = APIRouter(prefix="/historial", tags=["Historial"])


@router.get("/", response_model=List[HistorialResponse])
def listar_historial(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    return obtener_historial(db, skip=skip, limit=limit)
