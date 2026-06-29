from fastapi import APIRouter

router = APIRouter(prefix="/finanzas", tags=["finanzas"])


@router.get("/")
def read_finanzas():
    return {"status": "finanzas endpoint"}
