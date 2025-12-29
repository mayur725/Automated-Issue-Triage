
import os, json, random
from dotenv import load_dotenv
load_dotenv()
USE_OPENAI = os.getenv('USE_OPENAI','false').lower() == 'true'
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
DOCS_DIR = os.path.join(DATA_DIR, 'confluence_docs')
JIRA_FILE = os.path.join(DATA_DIR, 'resolved_jira.json')
EMB_FILE = os.path.join(DATA_DIR, 'embeddings.json')

def load_corpus():
    docs = []
    doc_names = []
    if os.path.exists(DOCS_DIR):
        for fn in sorted(os.listdir(DOCS_DIR)):
            p = os.path.join(DOCS_DIR, fn)
            with open(p, 'r', encoding='utf-8') as f:
                docs.append(f.read())
                doc_names.append(fn)
    jira = []
    if os.path.exists(JIRA_FILE):
        with open(JIRA_FILE,'r',encoding='utf-8') as f:
            jira = json.load(f)
    return docs, doc_names, jira

def compute_openai_embeddings(texts):
    import openai
    openai.api_key = OPENAI_API_KEY
    model = "text-embedding-3-small"
    resp = openai.Embedding.create(input=texts, model=model)
    return [r['embedding'] for r in resp['data']]

def main():
    docs, doc_names, jira = load_corpus()
    corpus = docs + [j['summary'] for j in jira]
    print(f"Loaded {len(corpus)} corpus items")
    if USE_OPENAI and OPENAI_API_KEY:
        try:
            embeddings = compute_openai_embeddings(corpus)
            out = {"doc_names": doc_names, "jira": jira, "embeddings": embeddings}
            with open(EMB_FILE,'w',encoding='utf-8') as f:
                json.dump(out, f)
            print("Saved embeddings to", EMB_FILE)
            return
        except Exception as e:
            print("OpenAI embedding failed:", e)
    embeddings = [[random.random() for _ in range(1536)] for _ in corpus]
    out = {"doc_names": doc_names, "jira": jira, "embeddings": embeddings}
    with open(EMB_FILE,'w',encoding='utf-8') as f:
        json.dump(out, f)
    print("Saved fallback embeddings to", EMB_FILE)

if __name__ == '__main__':
    main()
