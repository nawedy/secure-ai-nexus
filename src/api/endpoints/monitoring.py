from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.middleware.auth import authenticate_user, authorize_user

router = APIRouter()

@router.get("/monitoring")
async def monitoring_route(user = Depends(authorize_user)):
    #TODO: Implement monitoring route
    return {"message": "monitoring"}
