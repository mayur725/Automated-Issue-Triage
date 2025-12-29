
import os
import json
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from classifier import classify_ticket
from retriever import retrieve_doc_and_jira
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles

load_dotenv()

app = FastAPI(title="Automated Issue Triage Prototype")
app.mount('/', StaticFiles(directory=os.path.join(os.path.dirname(__file__), 'static'), html=True), name='static')

REQUEST_COUNTER = Counter('triage_requests_total', 'Total triage requests')
REQ_TIME = Histogram('triage_request_processing_seconds', 'Time spent processing triage request')

class Ticket(BaseModel):
    ticket_id: str
    short_desc: str = ""
    description: str = ""
    impact: str = "user"
    created: str = None

@app.post("/triage/single")
@REQ_TIME.time()
def triage_single(ticket: Ticket):
    REQUEST_COUNTER.inc()
    text = (ticket.short_desc or "") + "\n" + (ticket.description or "")
    try:
        result = classify_ticket(ticket.ticket_id, text)
        docs, jiras = retrieve_doc_and_jira(text, top_k=2)
        result['matched_doc'] = docs[0] if docs else None
        result['matched_jira'] = jiras
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/triage")
@REQ_TIME.time()
def triage_bulk(tickets: list[Ticket]):
    REQUEST_COUNTER.inc()
    outputs = []
    for t in tickets:
        text = (t.short_desc or "") + "\n" + (t.description or "")
        res = classify_ticket(t.ticket_id, text)
        docs, jiras = retrieve_doc_and_jira(text, top_k=2)
        res['matched_doc'] = docs[0] if docs else None
        res['matched_jira'] = jiras
        outputs.append(res)
    return outputs

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
