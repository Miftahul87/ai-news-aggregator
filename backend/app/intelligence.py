import re,hashlib
from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode
from datetime import datetime,timezone
TOPIC_KEYWORDS={
 "technology":["ai","artificial intelligence","software","chip","cyber","technology","robot","cloud"],
 "business":["market","business","company","economy","stock","trade","startup","revenue"],
 "science":["research","space","climate","scientist","study","energy","physics"],
 "world":["government","election","minister","war","diplomat","country","international"],
 "health":["health","hospital","medicine","disease","medical","vaccine"],
}
TRACKING={"utm_source","utm_medium","utm_campaign","utm_term","utm_content","fbclid","gclid"}
def canonicalize(url):
    p=urlsplit(url.strip())
    query=[(k,v) for k,v in parse_qsl(p.query,keep_blank_values=True) if k.lower() not in TRACKING]
    return urlunsplit((p.scheme.lower(),p.netloc.lower(),p.path.rstrip("/") or "/",urlencode(query),""))
def fingerprint(title,description):
    text=re.sub(r"\W+"," ",(title+" "+description).lower()).strip()
    return hashlib.sha256(text.encode()).hexdigest()
def topics_for(text):
    low=text.lower()
    return [topic for topic,words in TOPIC_KEYWORDS.items() if any(w in low for w in words)]
def extractive_summary(text,max_sentences=2):
    clean=re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",text or "")).strip()
    if not clean: return "Summary unavailable; open the original article for details."
    sentences=re.split(r"(?<=[.!?])\s+",clean)
    return " ".join(sentences[:max_sentences])[:600]
def relevance(title,description,published_at,source):
    score=1.0+0.25*len(topics_for(title+" "+description))
    if published_at:
        dt=published_at
        if dt.tzinfo is None: dt=dt.replace(tzinfo=timezone.utc)
        age=max(0,(datetime.now(timezone.utc)-dt).total_seconds()/3600)
        score+=max(0,2-age/48)
    return round(score,3)
