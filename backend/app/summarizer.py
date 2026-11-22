import httpx
from .config import settings
from .intelligence import extractive_summary
def summarize(title,content):
    # Optional OpenAI-compatible provider. Safe deterministic fallback is always available.
    if not (settings.llm_base_url and settings.llm_api_key and settings.llm_model):
        return extractive_summary(content)
    try:
        response=httpx.post(
            settings.llm_base_url.rstrip("/")+"/chat/completions",
            headers={"Authorization":f"Bearer {settings.llm_api_key}"},
            json={"model":settings.llm_model,"temperature":0.2,"messages":[
              {"role":"system","content":"Summarize the supplied news excerpt in at most two factual sentences. Do not add facts."},
              {"role":"user","content":f"Title: {title}\nExcerpt: {content[:6000]}"}]},
            timeout=20)
        response.raise_for_status()
        result=response.json()["choices"][0]["message"]["content"].strip()
        return result[:1000] if result else extractive_summary(content)
    except (httpx.HTTPError,KeyError,ValueError,TypeError):
        return extractive_summary(content)
