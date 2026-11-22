from datetime import datetime,timezone
from sqlalchemy import String,Text,DateTime,Boolean,Integer,Float,JSON,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from .database import Base
def now(): return datetime.now(timezone.utc)
class Article(Base):
    __tablename__="articles"
    __table_args__=(UniqueConstraint("canonical_url",name="uq_article_url"),)
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    title:Mapped[str]=mapped_column(String(500),index=True)
    canonical_url:Mapped[str]=mapped_column(String(1500))
    source:Mapped[str]=mapped_column(String(200),index=True)
    author:Mapped[str|None]=mapped_column(String(300),nullable=True)
    published_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True,index=True)
    description:Mapped[str]=mapped_column(Text,default="")
    summary:Mapped[str]=mapped_column(Text,default="")
    topics:Mapped[list]=mapped_column(JSON,default=list)
    fingerprint:Mapped[str]=mapped_column(String(64),index=True)
    relevance_score:Mapped[float]=mapped_column(Float,default=0)
    saved:Mapped[bool]=mapped_column(Boolean,default=False)
    read:Mapped[bool]=mapped_column(Boolean,default=False)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class IngestionRun(Base):
    __tablename__="ingestion_runs"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    status:Mapped[str]=mapped_column(String(20),default="RUNNING")
    started_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
    finished_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
    feeds_checked:Mapped[int]=mapped_column(Integer,default=0)
    articles_seen:Mapped[int]=mapped_column(Integer,default=0)
    articles_added:Mapped[int]=mapped_column(Integer,default=0)
    errors:Mapped[list]=mapped_column(JSON,default=list)
