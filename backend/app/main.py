from fastapi import FastAPI,Depends,BackgroundTasks,HTTPException,Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select,desc,func
from .database import Base,engine,get_db,SessionLocal
from .models import Article,IngestionRun
from .schemas import ArticleOut,RunOut
from .ingestion import ingest
from .summarizer import summarize
from .intelligence import topics_for
Base.metadata.create_all(bind=engine)
app=FastAPI(title="AI News Aggregator",version="1.0.0",description="Multi-source news ingestion, deduplication, topic intelligence and summaries.")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])
def run_ingestion():
    db=SessionLocal()
    try: ingest(db)
    finally: db.close()
@app.get("/health")
def health(db:Session=Depends(get_db)):
    db.execute(select(1)); return {"status":"ok","service":"ai-news-aggregator"}
@app.post("/api/ingest",status_code=202)
def trigger(background:BackgroundTasks):
    background.add_task(run_ingestion)
    return {"status":"accepted","message":"News ingestion started in background."}
@app.get("/api/articles",response_model=list[ArticleOut])
def articles(q:str|None=None,topic:str|None=None,source:str|None=None,
             saved:bool|None=None,limit:int=Query(30,ge=1,le=100),offset:int=Query(0,ge=0),
             db:Session=Depends(get_db)):
    stmt=select(Article)
    if q: stmt=stmt.where(Article.title.ilike(f"%{q}%") | Article.description.ilike(f"%{q}%"))
    if topic: stmt=stmt.where(Article.topics.contains([topic.lower()]))
    if source: stmt=stmt.where(Article.source.ilike(f"%{source}%"))
    if saved is not None: stmt=stmt.where(Article.saved==saved)
    stmt=stmt.order_by(desc(Article.relevance_score),desc(Article.published_at)).offset(offset).limit(limit)
    return list(db.scalars(stmt))
@app.get("/api/articles/{article_id}",response_model=ArticleOut)
def article(article_id:int,db:Session=Depends(get_db)):
    row=db.get(Article,article_id)
    if not row: raise HTTPException(404,"Article not found")
    return row
@app.post("/api/articles/{article_id}/save")
def save(article_id:int,db:Session=Depends(get_db)):
    row=db.get(Article,article_id)
    if not row: raise HTTPException(404,"Article not found")
    row.saved=True; db.commit(); return {"saved":True}
@app.delete("/api/articles/{article_id}/save")
def unsave(article_id:int,db:Session=Depends(get_db)):
    row=db.get(Article,article_id)
    if not row: raise HTTPException(404,"Article not found")
    row.saved=False; db.commit(); return {"saved":False}
@app.post("/api/articles/{article_id}/read")
def mark_read(article_id:int,db:Session=Depends(get_db)):
    row=db.get(Article,article_id)
    if not row: raise HTTPException(404,"Article not found")
    row.read=True; db.commit(); return {"read":True}
@app.get("/api/saved",response_model=list[ArticleOut])
def saved(db:Session=Depends(get_db)):
    return list(db.scalars(select(Article).where(Article.saved==True).order_by(desc(Article.created_at))))
@app.get("/api/analytics")
def analytics(db:Session=Depends(get_db)):
    total=db.scalar(select(func.count(Article.id))) or 0
    by_source=db.execute(select(Article.source,func.count(Article.id)).group_by(Article.source)).all()
    rows=list(db.scalars(select(Article)))
    topics={}
    for row in rows:
        for topic in row.topics or []: topics[topic]=topics.get(topic,0)+1
    return {"total_articles":total,"sources":[{"source":s,"count":c} for s,c in by_source],
      "topics":[{"topic":t,"count":c} for t,c in sorted(topics.items(),key=lambda x:x[1],reverse=True)],
      "saved_articles":sum(1 for r in rows if r.saved),"unread_articles":sum(1 for r in rows if not r.read)}
@app.get("/api/runs",response_model=list[RunOut])
def runs(limit:int=Query(20,ge=1,le=100),db:Session=Depends(get_db)):
    return list(db.scalars(select(IngestionRun).order_by(desc(IngestionRun.id)).limit(limit)))
