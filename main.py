from fastapi import FastAPI
from fastapi_routers.uploads import upload_link_doc as upl_doc_link
from fastapi_routers.display import display as dply
from fastapi_routers.db import db_manager as db
from fastapi_routers.Q_and_A import question_answering as q_a
from fastapi_routers.Q_and_A import srag_q_a_web as srag
from fastapi_routers.fine_tune_model import fine_tune_llm as ft

app = FastAPI()


@app.get('/')
async def root():
    return {"output": "nothing to see here"}


app.include_router(upl_doc_link.router)
app.include_router(dply.router)
app.include_router(db.router)
app.include_router(q_a.router)
app.include_router(ft.router)
app.include_router(srag.router)
