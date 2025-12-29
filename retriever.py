
import os, json
from dotenv import load_dotenv
load_dotenv()
USE_OPENAI = os.getenv('USE_OPENAI', 'false').lower() == 'true'
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
EMB_FILE = os.path.join(DATA_DIR, 'embeddings.json')
DOCS_DIR = os.path.join(DATA_DIR, 'confluence_docs')
JIRA_FILE = os.path.join(DATA_DIR, 'resolved_jira.json')

_corpus = []
_doc_names = []
_jira = []
if os.path.exists(DOCS_DIR):
    for fn in sorted(os.listdir(DOCS_DIR)):
        p = os.path.join(DOCS_DIR, fn)
        with open(p, 'r', encoding='utf-8') as f:
            _corpus.append(f.read())
            _doc_names.append(fn)
if os.path.exists(JIRA_FILE):
    with open(JIRA_FILE, 'r', encoding='utf-8') as f:
        _jira = json.load(f)

_embeddings = None
_emb_doc_names = []
_emb_jira = []
if os.path.exists(EMB_FILE):
    try:
        with open(EMB_FILE, 'r', encoding='utf-8') as f:
            emb_json = json.load(f)
            _embeddings = emb_json.get('embeddings')
            _emb_doc_names = emb_json.get('doc_names', [])
            _emb_jira = emb_json.get('jira', [])
    except Exception as e:
        print("Failed to load embeddings.json:", e)

def _local_retrieve(text, top_k=2):
    corpus = _corpus + [j['summary'] for j in _jira]
    if not corpus:
        return [], []
    vecs = TfidfVectorizer().fit_transform(corpus + [text])
    sims = cosine_similarity(vecs[-1], vecs[:-1])[0]
    idxs = sims.argsort()[::-1][:top_k]
    docs = []
    jiras = []
    for i in idxs:
        if i < len(_corpus):
            docs.append(_doc_names[i])
        else:
            j = _jira[i - len(_corpus)]
            jiras.append(j.get('id'))
    return docs, jiras

def _emb_retrieve(text, top_k=2):
    try:
        import openai, numpy as np
        openai.api_key = OPENAI_API_KEY
        model = "text-embedding-3-small"
        resp = openai.Embedding.create(input=[text], model=model)
        qemb = np.array(resp['data'][0]['embedding'])
        emb_matrix = np.array(_embeddings)
        norms = np.linalg.norm(emb_matrix, axis=1) * np.linalg.norm(qemb)
        sims = (emb_matrix @ qemb) / norms
        idxs = sims.argsort()[::-1][:top_k]
        docs = []
        jiras = []
        for i in idxs:
            if i < len(_emb_doc_names):
                docs.append(_emb_doc_names[i])
            else:
                j = _emb_jira[i - len(_emb_doc_names)]
                jiras.append(j.get('id'))
        return docs, jiras
    except Exception as e:
        print("Embedding retrieval failed:", e)
        return [], []

def retrieve_doc_and_jira(text, top_k=2):
    try:
        if USE_OPENAI and _embeddings:
            return _emb_retrieve(text, top_k=top_k)
    except Exception as e:
        print("Embedding path failed, fallback:", e)
    return _local_retrieve(text, top_k=top_k)
