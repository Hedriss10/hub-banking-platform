from fastapi import APIRouter
from src.interface.api.v2 import v2_router

app_router = APIRouter(prefix='/api')
router_list = [v2_router]

for router in router_list:
    app_router.include_router(router)
