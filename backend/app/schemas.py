from datetime import datetime
from pydantic import BaseModel,ConfigDict
class ArticleOut(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id:int; title:str; canonical_url:str; source:str; author:str|None
    published_at:datetime|None; description:str; summary:str; topics:list
    relevance_score:float; saved:bool; read:bool
class RunOut(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id:int; status:str; started_at:datetime; finished_at:datetime|None
    feeds_checked:int; articles_seen:int; articles_added:int; errors:list
