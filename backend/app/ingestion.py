from datetime import datetime,timezone
from dateutil import parser as dateparser
import feedparser,httpx
from sqlalchemy import select
from .config import settings
from .feeds import FEEDS
from .models import Article,IngestionRun
from .intelligence import canonicalize,fingerprint,topics_for,extractive_summary,relevance
def parse_date(value):
    if not value: return None
    try:
        dt=dateparser.parse(value)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except (ValueError,TypeError,OverflowError): return None
def fetch_feed(client,url):
    response=client.get(url); response.raise_for_status()
    return feedparser.parse(response.text)
def ingest(db,feeds=None,client=None):
    run=IngestionRun(status="RUNNING"); db.add(run); db.commit(); db.refresh(run)
    own=client is None
    client=client or httpx.Client(timeout=settings.ingest_timeout_seconds,headers={"User-Agent":"AI-News-Aggregator/1.0"})
    errors=[]; seen=added=checked=0
    try:
        for source,url in (feeds or FEEDS):
            checked+=1
            try:
                parsed=fetch_feed(client,url)
                for entry in parsed.entries[:settings.ingest_max_articles_per_feed]:
                    title=(entry.get("title") or "").strip()
                    link=entry.get("link") or ""
                    desc=entry.get("summary") or entry.get("description") or ""
                    if not title or not link: continue
                    seen+=1; canonical=canonicalize(link)
                    existing=db.scalar(select(Article).where(Article.canonical_url==canonical))
                    fp=fingerprint(title,desc)
                    if existing: continue
                    # Fingerprint check catches duplicate stories syndicated at different URLs.
                    duplicate=db.scalar(select(Article).where(Article.fingerprint==fp))
                    if duplicate: continue
                    published=parse_date(entry.get("published") or entry.get("updated"))
                    summary=extractive_summary(desc)
                    row=Article(title=title[:500],canonical_url=canonical,source=source,
                      author=(entry.get("author") or None),published_at=published,
                      description=desc[:12000],summary=summary,
                      topics=topics_for(title+" "+desc),fingerprint=fp,
                      relevance_score=relevance(title,desc,published,source))
                    db.add(row); added+=1
                db.commit()
            except Exception as exc:
                db.rollback(); errors.append({"source":source,"error":str(exc)[:300]})
        run=db.get(IngestionRun,run.id)
        run.feeds_checked=checked; run.articles_seen=seen; run.articles_added=added
        run.errors=errors; run.status="PARTIAL" if errors and added else ("FAILED" if errors else "SUCCEEDED")
        run.finished_at=datetime.now(timezone.utc); db.commit()
        return run
    except Exception:
        db.rollback()
        run=db.get(IngestionRun,run.id)
        run.status="FAILED"; run.finished_at=datetime.now(timezone.utc); db.commit()
        raise
    finally:
        if own: client.close()
