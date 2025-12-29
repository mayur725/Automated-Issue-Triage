
import os, json, re
from dotenv import load_dotenv
load_dotenv()
USE_OPENAI = os.getenv('USE_OPENAI','false').lower() == 'true'
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import numpy as np

SAMPLE_TRAIN = [
    ("User cannot login, 401 unauthorized after password reset", "login"),
    ("Login fails with 403", "login"),
    ("System is slow and pages take >10s to load", "performance"),
    ("Reports timing out during generation", "performance"),
    ("File upload fails with error unsupported filetype", "bug"),
    ("Unexpected exception when saving record", "bug"),
    ("Need DB config change for APAC region", "config"),
    ("Permission denied when accessing dashboard", "access")
]

VECTOR = TfidfVectorizer()
VECTOR.fit([s[0] for s in SAMPLE_TRAIN])
X = VECTOR.transform([s[0] for s in SAMPLE_TRAIN])
CLF = LogisticRegression()
CLF.fit(X, [s[1] for s in SAMPLE_TRAIN])

def _local_classify(text, ticket_id=None):
    x = VECTOR.transform([text])
    pred = CLF.predict(x)[0]
    probs = CLF.predict_proba(x)[0]
    conf = float(np.max(probs))
    priority = "P2"
    if pred == "login" or "unauthorized" in text.lower() or "down" in text.lower():
        priority = "P1"
    return {"ticket_id": ticket_id, "category": pred, "priority": priority, "confidence": conf, "explanation": "local-tfidf-classifier"}

def _parse_json_from_text(txt):
    import json, re
    m = re.search(r'\{.*\}', txt, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except:
        return None

def _openai_classify(text, ticket_id=None):
    try:
        import openai
        openai.api_key = OPENAI_API_KEY
        system = {"role":"system","content":"You are an automated triage assistant. Classify tickets into categories and provide priority."}
        user = {"role":"user","content":f"""Read the support ticket below and classify into one of: login, performance, bug, config, access, other.
Return only a JSON object with fields:
- category: one of ["login","performance","bug","config","access","other"]
- priority: one of ["P1","P2","P3"]
- confidence: a number between 0 and 1
- reason: short text why

Ticket:
""" + text}
        resp = openai.ChatCompletion.create(model="gpt-4o-mini", messages=[system,user], max_tokens=200, temperature=0)
        out = resp.choices[0].message.content
        data = _parse_json_from_text(out)
        if not data:
            comp = openai.Completion.create(engine="text-davinci-003", prompt=user['content'] + "\nRespond with JSON only.", max_tokens=150, temperature=0)
            data = _parse_json_from_text(comp.choices[0].text)
        if data:
            data['ticket_id'] = ticket_id
            return data
    except Exception as e:
        print("OpenAI classify error:", e)
    return None

def classify_ticket(ticket_id, text):
    if USE_OPENAI and OPENAI_API_KEY:
        try:
            r = _openai_classify(text, ticket_id)
            if r:
                return r
        except Exception as e:
            print("OpenAI classify failed, falling back:", e)
    return _local_classify(text, ticket_id)
