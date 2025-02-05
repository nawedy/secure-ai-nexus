from fastapi import APIRouter, Depends, HTTPException, status
from src.auth import authorize_user

router = APIRouter()

@router.get("/monitoring")
async def monitoring_route(user = Depends(authorize_user)):
    """
    Monitoring route.
    This route is protected.
    """
    return {"message": "monitoring"}
