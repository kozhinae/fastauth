from fastapi import FastAPI

from .database import engine, Base
from .routers import auth, profile, admin_acl, mock_business

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAuth - Custom Auth & ACL")

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(admin_acl.router)
app.include_router(mock_business.router)


@app.get("/")
def root():
    return {"msg": "FastAuth - API up"}
