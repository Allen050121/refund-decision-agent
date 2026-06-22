from fastapi import APIRouter

router = APIRouter()


@router.get("")
def health_check():
    return {"status": "OK"}


@router.get("/ready")
def readiness_check():
    # TODO: 检查依赖服务是否可用
    return {"status": "ready"}
