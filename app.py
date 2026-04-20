import streamlit as st
import anthropic
import pandas as pd
import json
import uuid
import io
import sqlite3
import os

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

st.set_page_config(
    page_title="Fusion Lab — CIS 360",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

:root {
    --bg:       #0a0a0f;
    --surface:  #111118;
    --surface2: #1a1a24;
    --border:   #2a2a38;
    --border2:  #3a3a50;
    --accent:   #7c6af7;
    --accent2:  #a594f9;
    --green:    #2dd4a0;
    --green2:   #1a8c68;
    --amber:    #f0a654;
    --red:      #f06a6a;
    --text:     #e8e8f0;
    --muted:    #8888a8;
    --faint:    #44445a;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background: var(--bg);
    color: var(--text);
}

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="collapsedControl"] { display: none !important; }
button[kind="header"] { display: none !important; }
[data-testid="stSidebarCollapseButton"] { display: none !important; }
section[data-testid="stSidebar"] { min-width: 320px !important; max-width: 320px !important; transform: none !important; }
section[data-testid="stSidebar"][aria-expanded="false"] { min-width: 320px !important; width: 320px !important; transform: none !important; margin-left: 0 !important; }
section[data-testid="stSidebar"] > div { min-width: 320px !important; }
[data-testid="stSidebarContent"] { min-width: 320px !important; }
.block-container { padding: 1rem 1.5rem 2rem !important; max-width: 100% !important; }
[data-testid="stSidebar"] { background: var(--surface) !important; border-right: 1px solid var(--border); }
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Tabs */
[data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
    padding: 0 !important;
}
[data-baseweb="tab"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
    background: transparent !important;
    border: none !important;
    padding: 10px 18px !important;
    white-space: nowrap !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    color: var(--accent2) !important;
    border-bottom: 2px solid var(--accent) !important;
}

/* Inputs */
input, textarea, [data-baseweb="input"] input, [data-baseweb="textarea"] textarea {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}
input:focus, textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(124,106,247,0.15) !important;
}

/* Buttons */
[data-testid="stButton"] button {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.05em !important;
    border-radius: 6px !important;
    transition: all 0.15s ease !important;
    white-space: normal !important;
    word-wrap: break-word !important;
    text-align: left !important;
    padding: 8px 12px !important;
    line-height: 1.4 !important;
    min-height: 40px !important;
    height: auto !important;
}
[data-testid="stButton"] button:hover {
    border-color: var(--accent) !important;
    color: var(--accent2) !important;
    background: rgba(124,106,247,0.08) !important;
}

/* Metrics */
[data-testid="metric-container"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
}
[data-testid="stMetricValue"] { color: var(--text) !important; font-family: 'DM Mono', monospace !important; }
[data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: 0.7rem !important; }

/* Dataframes */
[data-testid="stDataFrame"] { border: 1px solid var(--border) !important; border-radius: 8px !important; }

/* Form submit button */
[data-testid="stFormSubmitButton"] button {
    background: var(--accent) !important;
    border-color: var(--accent) !important;
    color: white !important;
    font-weight: 600 !important;
    width: 100% !important;
}
[data-testid="stFormSubmitButton"] button:hover {
    background: var(--accent2) !important;
    color: white !important;
}

/* Code blocks */
code, pre { font-family: 'DM Mono', monospace !important; background: var(--surface2) !important; color: var(--green) !important; }

/* Selectbox */
[data-baseweb="select"] > div {
    background: var(--surface2) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: var(--surface2) !important;
    border: 1px dashed var(--border2) !important;
    border-radius: 8px !important;
}

/* Custom components */
.lab-header {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.05rem;
    letter-spacing: 0.04em;
    color: var(--text);
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
}
.lab-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: var(--muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 16px;
}
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--faint);
    margin-bottom: 8px;
    margin-top: 4px;
}
.pill {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    padding: 2px 8px;
    border-radius: 20px;
    font-weight: 500;
    letter-spacing: 0.06em;
}
.pill-fusion { background: rgba(45,212,160,0.12); color: var(--green); border: 1px solid rgba(45,212,160,0.25); }
.pill-nonfusion { background: rgba(240,106,106,0.1); color: var(--red); border: 1px solid rgba(240,106,106,0.2); }

.paper-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 12px;
    margin-bottom: 8px;
    transition: border-color 0.15s;
}
.paper-card:hover { border-color: var(--border2); }
.paper-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--text);
    line-height: 1.4;
    word-wrap: break-word;
    overflow-wrap: break-word;
}
.paper-meta {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: var(--muted);
    margin-top: 4px;
}
.u-dots { display: flex; gap: 5px; margin-top: 6px; align-items: center; }
.u-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.u-label { font-family: 'DM Mono', monospace; font-size: 0.6rem; color: var(--faint); }

.msg-user {
    background: linear-gradient(135deg, #7c6af7, #5f4fd4);
    color: white;
    border-radius: 16px 16px 4px 16px;
    padding: 10px 14px;
    margin: 8px 0;
    font-size: 0.85rem;
    max-width: 80%;
    margin-left: auto;
    line-height: 1.5;
    word-wrap: break-word;
    overflow-wrap: break-word;
}
.msg-rn {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 4px 16px 16px 16px;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 0.85rem;
    max-width: 92%;
    color: var(--text);
    line-height: 1.6;
    word-wrap: break-word;
    overflow-wrap: break-word;
}
.msg-source {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: var(--green);
    border-left: 2px solid var(--green2);
    padding: 3px 8px;
    margin-top: 8px;
    background: rgba(45,212,160,0.06);
    border-radius: 0 4px 4px 0;
    display: inline-block;
    word-wrap: break-word;
    overflow-wrap: break-word;
    max-width: 100%;
}

.query-btn {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
    cursor: pointer;
    transition: all 0.15s;
    width: 100%;
}
.stat-bar {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px 16px;
    display: flex;
    gap: 24px;
    align-items: center;
    margin-bottom: 16px;
    flex-wrap: wrap;
}
.stat-item { text-align: center; }
.stat-num {
    font-family: 'Syne', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--accent2);
    line-height: 1;
}
.stat-lbl {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 12px 0;
}
.welcome-box {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 8px;
    padding: 20px 24px;
    margin: 16px 0;
}
.welcome-title {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 8px;
}
.welcome-text {
    font-size: 0.85rem;
    color: var(--muted);
    line-height: 1.7;
}
.welcome-example {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: var(--accent2);
    margin-top: 4px;
}
.stakeholder-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px;
    cursor: pointer;
    transition: all 0.15s;
    height: 100%;
}
.stakeholder-card:hover { border-color: var(--accent); background: rgba(124,106,247,0.05); }
.stakeholder-icon {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: var(--accent2);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.stakeholder-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--text);
    line-height: 1.3;
}
.sug-chip {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    background: rgba(124,106,247,0.08);
    border: 1px solid rgba(124,106,247,0.2);
    color: var(--accent2);
    border-radius: 20px;
    padding: 5px 12px;
    cursor: pointer;
    transition: all 0.15s;
    display: inline-block;
    margin: 3px;
    word-wrap: break-word;
    overflow-wrap: break-word;
    max-width: 100%;
    white-space: normal;
    line-height: 1.4;
}
.sug-chip:hover { background: rgba(124,106,247,0.18); border-color: var(--accent); color: white; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# DATABASE
# ==============================================================================
DB_PATH = "knowledge_graph.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS papers (
            DOI TEXT PRIMARY KEY, Title TEXT, Author TEXT, PublicationTitle TEXT,
            PublicationDate TEXT, URL TEXT, Keywords TEXT, Abstract TEXT,
            Publisher TEXT, FieldOfStudy TEXT, IsDataFusionPaper TEXT,
            DataFusionClassificationReason TEXT
        );
        CREATE TABLE IF NOT EXISTS fusion_methods (
            MethodKey TEXT PRIMARY KEY, MethodName TEXT, DOI TEXT, Description TEXT,
            U1 TEXT, U3 TEXT, OutputData TEXT,
            FOREIGN KEY (DOI) REFERENCES papers(DOI)
        );
        CREATE TABLE IF NOT EXISTS datasets (
            id INTEGER PRIMARY KEY AUTOINCREMENT, DOI TEXT, DataName TEXT,
            DatasetURL TEXT, MethodKey TEXT, DataType TEXT, SensorType TEXT,
            SpatialCoverage TEXT, TemporalCoverage TEXT, CollectionMethod TEXT,
            U2 TEXT, Format TEXT, License TEXT, Provenance TEXT,
            FOREIGN KEY (DOI) REFERENCES papers(DOI),
            FOREIGN KEY (MethodKey) REFERENCES fusion_methods(MethodKey)
        );
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT, content TEXT, source TEXT
        );
    """)
    conn.commit(); conn.close()

init_db()

def db_papers():
    conn = get_db(); rows = conn.execute("SELECT * FROM papers").fetchall(); conn.close()
    return [dict(r) for r in rows]

def db_methods():
    conn = get_db(); rows = conn.execute("SELECT * FROM fusion_methods").fetchall(); conn.close()
    return [dict(r) for r in rows]

def db_datasets():
    conn = get_db(); rows = conn.execute("SELECT * FROM datasets").fetchall(); conn.close()
    return [dict(r) for r in rows]

def db_messages():
    conn = get_db()
    rows = conn.execute("SELECT role, content, source FROM chat_messages ORDER BY id").fetchall()
    conn.close(); return [dict(r) for r in rows]

def db_count_u():
    conn = get_db()
    u1 = conn.execute("SELECT COUNT(*) FROM fusion_methods WHERE U1 != ''").fetchone()[0]
    u3 = conn.execute("SELECT COUNT(*) FROM fusion_methods WHERE U3 != ''").fetchone()[0]
    u2 = conn.execute("SELECT COUNT(*) FROM datasets WHERE U2 != ''").fetchone()[0]
    conn.close(); return u1 + u2 + u3

def db_insert_paper(p):
    conn = get_db()
    conn.execute("""INSERT OR REPLACE INTO papers
        (DOI,Title,Author,PublicationTitle,PublicationDate,URL,Keywords,Abstract,
         Publisher,FieldOfStudy,IsDataFusionPaper,DataFusionClassificationReason)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        (p["DOI"],p["Title"],p["Author"],p["PublicationTitle"],p["PublicationDate"],
         p["URL"],p["Keywords"],p["Abstract"],p["Publisher"],p["FieldOfStudy"],
         p["IsDataFusionPaper"],p["DataFusionClassificationReason"]))
    conn.commit(); conn.close()

def db_insert_method(m):
    conn = get_db()
    conn.execute("""INSERT OR REPLACE INTO fusion_methods
        (MethodKey,MethodName,DOI,Description,U1,U3,OutputData) VALUES (?,?,?,?,?,?,?)""",
        (m["MethodKey"],m["MethodName"],m["DOI"],m["Description"],m["U1"],m["U3"],m["OutputData"]))
    conn.commit(); conn.close()

def db_insert_dataset(d):
    conn = get_db()
    conn.execute("""INSERT INTO datasets
        (DOI,DataName,DatasetURL,MethodKey,DataType,SensorType,SpatialCoverage,
         TemporalCoverage,CollectionMethod,U2,Format,License,Provenance)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (d["DOI"],d["DataName"],d["DatasetURL"],d["MethodKey"],d["DataType"],
         d["SensorType"],d["SpatialCoverage"],d["TemporalCoverage"],
         d["CollectionMethod"],d["U2"],d["Format"],d["License"],d["Provenance"]))
    conn.commit(); conn.close()

def db_add_message(role, content, source=""):
    conn = get_db()
    conn.execute("INSERT INTO chat_messages (role,content,source) VALUES (?,?,?)", (role,content,source))
    conn.commit(); conn.close()

def db_clear():
    conn = get_db()
    conn.executescript("DELETE FROM datasets; DELETE FROM fusion_methods; DELETE FROM papers; DELETE FROM chat_messages;")
    conn.commit(); conn.close()

DEMO_QUERIES = {
    "Linkage — methods & datasets": """SELECT fm.MethodName, fm.MethodKey, d.DataName, d.DataType, p.Title AS Paper
FROM fusion_methods fm
JOIN datasets d ON fm.MethodKey = d.MethodKey
JOIN papers p   ON fm.DOI = p.DOI
ORDER BY fm.MethodName, d.DataName;""",

    "Uncertainty — U2 by data type": """SELECT d.DataType, d.DataName, d.U2, p.Title AS Paper
FROM datasets d
JOIN papers p ON d.DOI = p.DOI
WHERE d.U2 != ''
ORDER BY d.DataType, d.DataName;""",

    "Discovery — most connected dataset": """SELECT d.DataName,
       COUNT(DISTINCT d.MethodKey) AS MethodCount,
       COUNT(DISTINCT d.DOI)       AS PaperCount
FROM datasets d
WHERE d.MethodKey != ''
GROUP BY d.DataName
ORDER BY MethodCount DESC LIMIT 10;""",

    "Traffic-related methods": """SELECT fm.MethodName, fm.Description, d.DataName, d.DataType, p.Title AS Paper
FROM fusion_methods fm
JOIN datasets d ON fm.MethodKey = d.MethodKey
JOIN papers p   ON fm.DOI = p.DOI
WHERE LOWER(fm.Description) LIKE '%traffic%'
   OR LOWER(d.DataName)     LIKE '%traffic%'
   OR LOWER(d.DataType)     LIKE '%traffic%';""",

    "Satellite U2 uncertainty": """SELECT p.Title AS Paper, d.DataName, d.SensorType, d.U2
FROM datasets d
JOIN papers p ON d.DOI = p.DOI
WHERE LOWER(d.DataType) LIKE '%satellite%' AND d.U2 != '';""",
}

# ==============================================================================
# SESSION STATE
# ==============================================================================
# Auto-load API key from Streamlit Cloud secrets if available
_default_key = ""
try:
    _default_key = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    pass

for k, v in {"api_key": _default_key, "suggestions": [], "show_sug": True, "selected_doi": "all"}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ==============================================================================
# HELPERS
# ==============================================================================
def get_client():
    key = st.session_state.api_key
    return anthropic.Anthropic(api_key=key) if key else None

def call_api(prompt, max_tokens=2000):
    client = get_client()
    if not client:
        st.error("Enter your API key in the sidebar first.")
        st.stop()
    msg = client.messages.create(
        model="claude-sonnet-4-20250514", max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}])
    return msg.content[0].text

def extract_text_from_pdf(f):
    if not PdfReader:
        st.error("Run: py -m pip install pypdf"); return ""
    try:
        r = PdfReader(io.BytesIO(f.read()))
        return "".join(p.extract_text() or "" for p in r.pages).strip()
    except Exception as e:
        st.error(f"PDF read error: {e}"); return ""

EXTRACT_PROMPT = """Extract structured knowledge graph data from this research paper.
Only extract information explicitly stated. Never hallucinate.

CRITICAL UNCERTAINTY EXTRACTION RULES - read carefully:

U1 (Conception uncertainty): Ambiguity in how the real-world phenomenon is DEFINED or ABSTRACTED.
Look for: vague definitions, subjective classifications, ambiguous scope, assumptions about what counts as an event.
Example phrases: "assumed to", "defined as", "considered as", "approximated as", "treated as constant"

U2 (Measurement uncertainty): Problems with HOW DATA WAS COLLECTED or MEASURED.
This is the most commonly missed field. Search the ENTIRE paper for ANY of these:
- Sensor limitations, sensor errors, noise, signal interference
- Missing data, data gaps, removed data entries, filtered outliers
- Spatial resolution limits, temporal resolution limits, sampling frequency mismatches
- Approximations used because direct measurement was unavailable
- Interpolation between measurement stations
- Data collected from a different location/time than where it was needed
- Privacy alterations, anonymization affecting data
- Proxy measurements used instead of direct measurements
Example phrases: "missing values were removed", "linear approximation", "sampled yearly but needed monthly",
"some areas do not cover any station", "approximated correspondingly", "not directly measured",
"collected from nearby stations", "resolution", "noise", "signal-to-noise"

U3 (Analysis uncertainty): Limitations of the ALGORITHM or MODEL itself.
THIS IS THE MOST IMPORTANT FIELD FOR FUSION METHODS. Every machine learning or algorithmic paper
has U3 uncertainty — no model is perfect. Search for ALL of these:
- Model assumes something about the data (linear degradation, Gaussian noise, stationarity)
- Results only tested on specific datasets, may not generalize
- Deep learning / neural network is a black box
- Overfitting risk, dropout used to prevent overfitting
- Performance degrades at high missing rates or edge cases
- Computational constraints limit model size or depth
- Author explicitly states limitations or future work
- Model only suitable for specific conditions (e.g. "only suitable for CNC lathe")
- Tucker decomposition "not suitable for large-scale tensors"
- Training data bias, small dataset size
Example phrases: "may not generalize", "limited to", "only suitable for", "black-box", "assumes",
"future work", "limitation", "constrained by", "dataset is limited", "not suitable for",
"performance degrades", "low universality", "further research needed"

Do NOT leave U3 empty. Every fusion method paper has model limitations — find them.

For EVERY dataset, search the full paper text for any mention of that dataset having
measurement problems, approximations, missing data, or collection limitations.
Do NOT leave U2 empty unless the paper truly says nothing about data quality for that dataset.

Return ONLY valid JSON, no markdown:
{{
  "doi_sheet": {{
    "DOI": "", "Title": "", "Author": "", "PublicationTitle": "",
    "PublicationDate": "", "URL": "", "Keywords": "", "Abstract": "",
    "Publisher": "", "FieldOfStudy": "",
    "IsDataFusionPaper": "Yes or No",
    "DataFusionClassificationReason": "one sentence"
  }},
  "fusion_methods": [{{
    "MethodName": "", "MethodKey": "UUID v4", "DOI": "",
    "Description": "max 130 chars",
    "U1": "Quote or describe the conception uncertainty from the paper, or empty string",
    "U3": "Quote or describe the analysis uncertainty from the paper, or empty string",
    "OutputData": ""
  }}],
  "datasets": [{{
    "DOI": "", "DataName": "", "DatasetURL": "", "MethodKey": "",
    "DataType": "", "SensorType": "", "SpatialCoverage": "",
    "TemporalCoverage": "", "CollectionMethod": "",
    "U2": "Quote or describe the measurement uncertainty for THIS dataset from the paper. Check for missing data, approximations, resolution limits, interpolation, sensor noise. Do NOT leave empty if any such issue is mentioned.",
    "Format": "", "License": "", "Provenance": ""
  }}]
}}

Text: {text}"""

SUGGEST_PROMPT = """Based on this knowledge graph, generate exactly 5 short specific research queries.
Reference actual method names, dataset names, or domains. Be specific, not generic.
Each time this is called, generate DIFFERENT questions than before - vary the focus, angle, and specificity.
Focus on: {focus}
Return ONLY a JSON array of 5 strings, no markdown.

Graph: {summary}"""

QUERY_SYSTEM = """You are the Research Navigator for a CIS 360 data fusion knowledge graph.

RULES: Answer ONLY from the graph data. Never invent. Cite paper titles. Reference exact names.
End every response with "Source: [paper title(s)]"

SCHEMA:
- papers: DOI PK, Title, Author, FieldOfStudy, IsDataFusionPaper
- fusion_methods: MethodKey PK, MethodName, DOI FK, Description, U1, U3, OutputData
- datasets: id PK, DOI FK, DataName, MethodKey FK, DataType, SensorType, SpatialCoverage, TemporalCoverage, U2

Knowledge Graph: {graph}"""

U3_PROMPT = """You are analyzing a research paper to extract U3 (Analysis Uncertainty) tags.
U3 = limitations of the ALGORITHM or MODEL itself.

For each fusion method listed below, find the U3 uncertainty from the paper text.
Search the conclusions, discussion, limitations, and future work sections specifically.

Look for ANY of:
- Model only tested on specific datasets, may not generalize
- Deep learning is a black box, cannot explain decisions
- Assumes specific data properties (linear, Gaussian, stationary)
- Performance degrades in edge cases or high missing-data scenarios
- Tucker/matrix decomposition not suitable for large-scale data
- Training data is limited or small
- Hyperparameters require manual tuning
- Author states future work or open problems
- Computational cost limits applicability
- Model bias toward majority class

Methods to tag: {methods}

Paper text (end section — conclusions/discussion/limitations):
{end_text}

Return ONLY a JSON object mapping MethodName to U3 string. If genuinely none found, use empty string.
Example: {{"M-LSTM": "Black-box deep learning model cannot explain feature importance; only tested on UK fleet data", "Cox PHM": "Assumes proportional hazards which may not hold for all failure types"}}
"""

def extract_paper(text):
    # Step 1: Main extraction using first + last sections
    if len(text) > 16000:
        combined = text[:10000] + "\n\n[...middle section omitted...]\n\n" + text[-6000:]
    else:
        combined = text
    raw = call_api(EXTRACT_PROMPT.format(text=combined), 2500)
    parsed = json.loads(raw.replace("```json","").replace("```","").strip())

    # Step 2: Focused U3 pass — send only the last 8000 chars targeting conclusions/limitations
    methods = parsed.get("fusion_methods", [])
    if methods:
        method_names = [m.get("MethodName","") for m in methods]
        end_text = text[-8000:] if len(text) > 8000 else text
        try:
            u3_raw = call_api(U3_PROMPT.format(
                methods=", ".join(method_names),
                end_text=end_text
            ), 800)
            u3_map = json.loads(u3_raw.replace("```json","").replace("```","").strip())
            # Merge U3 back into methods — override empty ones, keep existing if already filled
            for m in methods:
                name = m.get("MethodName","")
                existing_u3 = m.get("U3","")
                new_u3 = u3_map.get(name,"") or u3_map.get(name.split()[0],"")
                if new_u3 and not existing_u3:
                    m["U3"] = new_u3
                elif new_u3 and existing_u3:
                    pass  # keep existing
        except Exception:
            pass  # if second pass fails, keep whatever was extracted in step 1

    return parsed

def ingest_parsed(parsed):
    ds = parsed.get("doi_sheet", {})
    doi   = ds.get("DOI", str(uuid.uuid4())[:8])
    title = ds.get("Title", "") or "Untitled"
    db_insert_paper({
        "DOI": doi, "Title": title, "Author": ds.get("Author",""),
        "PublicationTitle": ds.get("PublicationTitle",""), "PublicationDate": ds.get("PublicationDate",""),
        "URL": ds.get("URL",""), "Keywords": ds.get("Keywords",""), "Abstract": ds.get("Abstract",""),
        "Publisher": ds.get("Publisher",""), "FieldOfStudy": ds.get("FieldOfStudy",""),
        "IsDataFusionPaper": ds.get("IsDataFusionPaper",""),
        "DataFusionClassificationReason": ds.get("DataFusionClassificationReason",""),
    })
    for m in parsed.get("fusion_methods", []):
        db_insert_method({
            "MethodKey": m.get("MethodKey", str(uuid.uuid4())), "MethodName": m.get("MethodName",""),
            "DOI": doi, "Description": m.get("Description",""), "U1": m.get("U1",""),
            "U3": m.get("U3",""), "OutputData": m.get("OutputData",""),
        })
    for d in parsed.get("datasets", []):
        db_insert_dataset({
            "DOI": doi, "DataName": d.get("DataName",""), "DatasetURL": d.get("DatasetURL",""),
            "MethodKey": d.get("MethodKey",""), "DataType": d.get("DataType",""),
            "SensorType": d.get("SensorType",""), "SpatialCoverage": d.get("SpatialCoverage",""),
            "TemporalCoverage": d.get("TemporalCoverage",""), "CollectionMethod": d.get("CollectionMethod",""),
            "U2": d.get("U2",""), "Format": d.get("Format",""), "License": d.get("License",""),
            "Provenance": d.get("Provenance",""),
        })
    return doi, title, ds

def refresh_suggestions():
    import random, time
    sel = st.session_state.get("selected_doi", "all")
    all_methods  = db_methods()
    all_datasets = db_datasets()
    if sel != "all":
        methods  = [m for m in all_methods  if m["DOI"] == sel]
        datasets = [d for d in all_datasets if d["DOI"] == sel]
    else:
        methods, datasets = all_methods, all_datasets
    if not methods and not datasets: return []
    summary = json.dumps({
        "methods": [{"name": m["MethodName"],
                     "datasets": [d["DataName"] for d in datasets if d["MethodKey"] == m["MethodKey"]]}
                    for m in methods],
        "datasets": [{"name": d["DataName"], "type": d["DataType"], "sensor": d["SensorType"]}
                     for d in datasets],
    })[:2000]
    focuses = [
        "uncertainty and data quality limitations",
        "cross-paper dataset comparisons and sensor types",
        "method performance and algorithmic tradeoffs",
        "spatial and temporal coverage gaps",
        "data fusion architecture and integration approaches",
        "practical deployment and real-world applicability",
        "which methods work best for which data types",
        "sensor accuracy and measurement error",
        "geographic and temporal scope of datasets",
        "how different papers handle missing or noisy data",
    ]
    focus = random.choice(focuses)
    seed  = random.randint(1000, 9999)
    prompt = (
        f"[Request #{seed}] Based on this knowledge graph, generate exactly 5 SHORT research questions "
        f"(under 12 words each). Each question must be UNIQUE and DIFFERENT from any previous set. "
        f"Focus specifically on: {focus}. "
        f"Use exact names from the graph data. Do not use generic phrases. "
        f"Return ONLY a valid JSON array of 5 strings, nothing else.\n\nGraph: {summary}"
    )
    try:
        raw = call_api(prompt, 500)
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        return json.loads(cleaned.strip())
    except:
        return []

def query_graph(q):
    all_papers   = db_papers()
    all_methods  = db_methods()
    all_datasets = db_datasets()
    sel = st.session_state.get("selected_doi", "all")
    if sel != "all":
        papers_f   = [p for p in all_papers   if p["DOI"] == sel]
        methods_f  = [m for m in all_methods  if m["DOI"] == sel]
        datasets_f = [d for d in all_datasets if d["DOI"] == sel]
    else:
        papers_f, methods_f, datasets_f = all_papers, all_methods, all_datasets
    # Build a smart compact graph that keeps ALL uncertainty fields visible
    # rather than blindly truncating JSON which cuts off U2/U3 values
    def trim(s, n=120): return (s[:n] + "...") if s and len(s) > n else (s or "")

    compact_papers = [
        {"DOI": p["DOI"], "Title": p["Title"], "Author": p.get("Author",""),
         "FieldOfStudy": p.get("FieldOfStudy",""), "IsDataFusion": p.get("IsDataFusionPaper",""),
         "Year": p.get("PublicationDate","")}
        for p in papers_f
    ]
    compact_methods = [
        {"MethodKey": m["MethodKey"], "MethodName": m["MethodName"], "DOI": m["DOI"],
         "Description": trim(m.get("Description",""), 100),
         "U1": trim(m.get("U1",""), 200),
         "U3": trim(m.get("U3",""), 200)}
        for m in methods_f
    ]
    compact_datasets = [
        {"id": d["id"], "DOI": d["DOI"], "DataName": d["DataName"],
         "MethodKey": d.get("MethodKey",""), "DataType": d.get("DataType",""),
         "SensorType": d.get("SensorType",""),
         "SpatialCoverage": trim(d.get("SpatialCoverage",""), 60),
         "TemporalCoverage": trim(d.get("TemporalCoverage",""), 60),
         "U2": trim(d.get("U2",""), 250)}
        for d in datasets_f
    ]
    graph = json.dumps({
        "papers": compact_papers,
        "fusion_methods": compact_methods,
        "datasets": compact_datasets
    })
    # Only truncate if truly enormous (>20k chars)
    if len(graph) > 20000:
        graph = graph[:20000]
    raw = call_api(QUERY_SYSTEM.format(graph=graph) + f"\n\nQuery: {q}", 1500)
    lines = raw.split("\n")
    src_idx = next((i for i,l in enumerate(lines) if l.lower().startswith("source:")), None)
    if src_idx is not None:
        src  = lines[src_idx].replace("Source:","").replace("source:","").strip()
        main = "\n".join(l for i,l in enumerate(lines) if i != src_idx).strip()
    else:
        src, main = "", raw.strip()
    return main, src

def run_sql(sql):
    conn = get_db()
    try:
        rows = conn.execute(sql).fetchall()
        conn.close()
        return pd.DataFrame([dict(r) for r in rows]) if rows else pd.DataFrame()
    except Exception as e:
        conn.close(); return str(e)

def to_csv(records):
    return pd.DataFrame(records).to_csv(index=False).encode("utf-8")

def build_graph_html():
    papers   = db_papers()
    methods  = db_methods()
    datasets = db_datasets()
    nodes, edges, node_ids = [], [], set()
    for p in papers:
        nid = f"paper_{p['DOI']}"
        if nid not in node_ids:
            nodes.append({"id": nid, "label": p["Title"][:32]+("…" if len(p["Title"])>32 else ""),
                          "type": "paper", "detail": p["Title"]})
            node_ids.add(nid)
    for m in methods:
        nid = f"method_{m['MethodKey']}"
        if nid not in node_ids:
            nodes.append({"id": nid, "label": m["MethodName"][:28]+("…" if len(m["MethodName"])>28 else ""),
                          "type": "method", "detail": m["Description"]})
            node_ids.add(nid)
        pnid = f"paper_{m['DOI']}"
        if pnid in node_ids: edges.append({"source": pnid, "target": nid, "label": "describes"})
    for d in datasets:
        nid = f"dataset_{d['DataName']}_{d['DOI']}"
        if nid not in node_ids:
            nodes.append({"id": nid, "label": d["DataName"][:26]+("…" if len(d["DataName"])>26 else ""),
                          "type": "dataset",
                          "detail": f"Type: {d['DataType']} | Sensor: {d['SensorType'] or 'N/A'}"})
            node_ids.add(nid)
        mnid = f"method_{d['MethodKey']}"
        if mnid in node_ids: edges.append({"source": mnid, "target": nid, "label": "applied to"})
        pnid = f"paper_{d['DOI']}"
        if pnid in node_ids: edges.append({"source": pnid, "target": nid, "label": "references"})
    nj = json.dumps(nodes); ej = json.dumps(edges)
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ background:#0a0a0f; font-family:'DM Mono',monospace; position:relative; }}
#g {{ width:100%; height:560px; cursor:grab; }}
#g:active {{ cursor:grabbing; }}
.legend {{ display:flex; gap:20px; padding:10px 16px; font-size:11px; color:#8888a8;
           background:#111118; border-bottom:1px solid #2a2a38; align-items:center; }}
.ld {{ width:10px; height:10px; border-radius:50%; display:inline-block; margin-right:5px; }}
#tt {{ position:absolute; background:#1a1a24; border:1px solid #3a3a50; border-radius:8px;
       padding:8px 12px; font-size:11px; color:#e8e8f0; pointer-events:none; display:none;
       max-width:240px; line-height:1.5; }}
#info {{ padding:8px 16px; font-size:10px; color:#44445a; background:#111118;
         border-top:1px solid #2a2a38; letter-spacing:0.08em; }}
</style></head><body>
<div class="legend">
  <span><span class="ld" style="background:#2dd4a0"></span>Paper</span>
  <span><span class="ld" style="background:#a594f9"></span>Fusion Method</span>
  <span><span class="ld" style="background:#f0a654"></span>Dataset</span>
  <span style="margin-left:auto">drag to rearrange — hover for details</span>
</div>
<div id="tt"></div>
<svg id="g"></svg>
<div id="info">{len(nodes)} nodes &nbsp;·&nbsp; {len(edges)} edges &nbsp;·&nbsp; knowledge_graph.db</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<script>
const nodes={nj}, edges={ej};
const W=document.getElementById('g').clientWidth||900, H=560;
const svg=d3.select('#g').attr('viewBox',`0 0 ${{W}} ${{H}}`);
const color={{paper:'#2dd4a0',method:'#a594f9',dataset:'#f0a654'}};
const radius={{paper:20,method:15,dataset:12}};
const defs=svg.append('defs');
['paper','method','dataset'].forEach(t=>{{
  defs.append('marker').attr('id',`arr-${{t}}`).attr('viewBox','0 0 10 10')
    .attr('refX',8).attr('refY',5).attr('markerWidth',5).attr('markerHeight',5)
    .attr('orient','auto-start-reverse')
    .append('path').attr('d','M2 1L8 5L2 9').attr('fill','none')
    .attr('stroke',color[t]).attr('stroke-width',1.5)
    .attr('stroke-linecap','round').attr('stroke-linejoin','round');
}});
const sim=d3.forceSimulation(nodes)
  .force('link',d3.forceLink(edges).id(d=>d.id).distance(130).strength(0.5))
  .force('charge',d3.forceManyBody().strength(-380))
  .force('center',d3.forceCenter(W/2,H/2))
  .force('collision',d3.forceCollide().radius(d=>radius[d.type]+24));

// Single wrapper group — zoom transform applies here only
const g = svg.append('g').attr('class','graph-root');

const link=g.append('g').selectAll('line').data(edges).join('line')
  .attr('stroke',d=>{{const s=nodes.find(n=>n.id===(typeof d.source==='object'?d.source.id:d.source));return s?color[s.type]:'#444';}})
  .attr('stroke-width',1).attr('stroke-opacity',0.4)
  .attr('marker-end',d=>{{const s=nodes.find(n=>n.id===(typeof d.source==='object'?d.source.id:d.source));return s?`url(#arr-${{s.type}})`:'none';}});
const node=g.append('g').selectAll('g').data(nodes).join('g').style('cursor','grab')
  .call(d3.drag()
    .filter(e=>!e.ctrlKey && !e.button)
    .on('start',(e,d)=>{{if(!e.active)sim.alphaTarget(0.3).restart();d.fx=d.x;d.fy=d.y;}})
    .on('drag',(e,d)=>{{d.fx=e.x;d.fy=e.y;}})
    .on('end',(e,d)=>{{if(!e.active)sim.alphaTarget(0);d.fx=null;d.fy=null;}}));
node.append('circle').attr('r',d=>radius[d.type])
  .attr('fill',d=>color[d.type]+'22').attr('stroke',d=>color[d.type])
  .attr('stroke-width',1.5);
node.append('text').text(d=>d.label).attr('text-anchor','middle')
  .attr('dy',d=>radius[d.type]+14).attr('font-size','9px').attr('fill','#8888a8')
  .attr('font-family','DM Mono,monospace');
const tt=document.getElementById('tt');
node.on('mouseover',(e,d)=>{{tt.style.display='block';
  tt.innerHTML=`<strong style="color:${{color[d.type]}}">${{d.type}}</strong><br>${{d.detail||d.label}}`;
}}).on('mousemove',e=>{{tt.style.left=(e.pageX+14)+'px';tt.style.top=(e.pageY-30)+'px';}})
  .on('mouseout',()=>{{tt.style.display='none';}});
sim.on('tick',()=>{{
  link.attr('x1',d=>d.source.x).attr('y1',d=>d.source.y)
    .attr('x2',d=>{{const dx=d.target.x-d.source.x,dy=d.target.y-d.source.y,dist=Math.sqrt(dx*dx+dy*dy)||1;return d.target.x-(dx/dist)*(radius[d.target.type]+4);}})
    .attr('y2',d=>{{const dx=d.target.x-d.source.x,dy=d.target.y-d.source.y,dist=Math.sqrt(dx*dx+dy*dy)||1;return d.target.y-(dy/dist)*(radius[d.target.type]+4);}});
  node.attr('transform',d=>`translate(${{d.x}},${{d.y}})`);
}});

// Zoom & pan — only moves the graph-root group
const zoom = d3.zoom()
  .scaleExtent([0.15, 5])
  .on('zoom', (e) => {{
    g.attr('transform', e.transform);
  }});
svg.call(zoom);

// Zoom button controls
function zoomBy(factor) {{
  svg.transition().duration(250).call(zoom.scaleBy, factor);
}}
function resetZoom() {{
  svg.transition().duration(350).call(zoom.transform, d3.zoomIdentity);
}}

// Keyboard shortcuts
svg.on('keydown', (e) => {{
  if(e.key==='+' || e.key==='=') zoomBy(1.3);
  if(e.key==='-') zoomBy(0.77);
  if(e.key==='0') resetZoom();
}});
</script>
<div id="zoombtns" style="position:absolute;bottom:14px;right:16px;display:flex;gap:6px;z-index:10">
  <button onclick="zoomBy(1.3)" title="Zoom in" style="background:#1a1a24;border:1px solid #3a3a50;color:#a594f9;border-radius:6px;width:32px;height:32px;font-size:16px;cursor:pointer;display:flex;align-items:center;justify-content:center;font-family:DM Mono,monospace">+</button>
  <button onclick="zoomBy(0.77)" title="Zoom out" style="background:#1a1a24;border:1px solid #3a3a50;color:#a594f9;border-radius:6px;width:32px;height:32px;font-size:16px;cursor:pointer;display:flex;align-items:center;justify-content:center;font-family:DM Mono,monospace">-</button>
  <button onclick="resetZoom()" title="Reset zoom" style="background:#1a1a24;border:1px solid #3a3a50;color:#8888a8;border-radius:6px;padding:0 10px;height:32px;font-size:10px;cursor:pointer;font-family:DM Mono,monospace;letter-spacing:0.06em">RESET</button>
</div>
</body></html>"""

# ==============================================================================
# SIDEBAR
# ==============================================================================
with st.sidebar:
    st.markdown('<div class="lab-header">Fusion Lab</div>', unsafe_allow_html=True)
    st.markdown('<div class="lab-sub">CIS 360 / Knowledge Graph</div>', unsafe_allow_html=True)



    # Stats
    papers   = db_papers()
    methods  = db_methods()
    datasets = db_datasets()
    st.markdown(f"""
    <div class="stat-bar">
        <div class="stat-item"><div class="stat-num">{len(papers)}</div><div class="stat-lbl">Papers</div></div>
        <div class="stat-item"><div class="stat-num">{len(methods)}</div><div class="stat-lbl">Methods</div></div>
        <div class="stat-item"><div class="stat-num">{len(datasets)}</div><div class="stat-lbl">Datasets</div></div>
        <div class="stat-item"><div class="stat-num">{db_count_u()}</div><div class="stat-lbl">U-tags</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Ingest
    st.markdown('<div class="section-label">Ingest paper</div>', unsafe_allow_html=True)
    mode = st.radio("mode", ["Upload PDF", "Paste text"], horizontal=True, label_visibility="collapsed")

    with st.form("ingest", clear_on_submit=True):
        if mode == "Upload PDF":
            pdf_file = st.file_uploader("PDF", type=["pdf"], label_visibility="collapsed")
            paste    = None
        else:
            pdf_file = None
            paste    = st.text_area("text", placeholder="Paste abstract + methods...", height=110, label_visibility="collapsed")
        submitted = st.form_submit_button("Extract & Save", use_container_width=True)

    if submitted:
        if not st.session_state.api_key:
            st.error("Enter API key first.")
        else:
            text = ""
            if mode == "Upload PDF":
                if not pdf_file: st.error("Upload a PDF first."); st.stop()
                with st.spinner("Reading PDF..."):
                    text = extract_text_from_pdf(pdf_file)
                if not text: st.error("Could not read PDF. Try paste mode."); st.stop()
            else:
                text = paste or ""
                if not text: st.error("Paste some text first."); st.stop()

            with st.spinner("Extracting schema fields..."):
                try:
                    parsed = extract_paper(text)
                    doi, title, ds = ingest_parsed(parsed)
                    fuse = ds.get("IsDataFusionPaper","") == "Yes"
                    nm = len(parsed.get("fusion_methods",[]))
                    nd = len(parsed.get("datasets",[]))
                    db_add_message("rn",
                        f"**{title}** saved to database.\n\n"
                        f"{'✓ Data fusion confirmed' if fuse else '✗ Non-fusion'}: {ds.get('DataFusionClassificationReason','')}\n\n"
                        f"{nm} method(s) extracted with U1/U3 tags\n"
                        f"{nd} dataset(s) extracted with U2 tags\n\n"
                        f"Check the Graph tab to see the updated knowledge graph.", title)
                    with st.spinner("Generating suggestions..."):
                        try: st.session_state.suggestions = refresh_suggestions()
                        except: pass
                    st.rerun()
                except Exception as e:
                    st.error(f"Extraction failed: {e}")

    # Loaded papers — clickable selectors
    if papers:
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Select paper to focus on</div>', unsafe_allow_html=True)

        # All papers button
        sel = st.session_state.get("selected_doi", "all")
        all_active = sel == "all"
        if st.button(
            ("[ ALL PAPERS ]" if all_active else "All papers"),
            key="sel_all",
            use_container_width=True
        ):
            st.session_state.selected_doi = "all"
            st.session_state.suggestions = []
            st.rerun()

        for p in papers:
            has_u1 = any(m["U1"] for m in methods  if m["DOI"] == p["DOI"])
            has_u2 = any(d["U2"] for d in datasets if d["DOI"] == p["DOI"])
            has_u3 = any(m["U3"] for m in methods  if m["DOI"] == p["DOI"])
            fuse   = p["IsDataFusionPaper"] == "Yes"
            is_selected = sel == p["DOI"]
            pill   = '<span class="pill pill-fusion">fusion</span>' if fuse else '<span class="pill pill-nonfusion">non-fusion</span>'
            border_color = "#7c6af7" if is_selected else "var(--border)"
            bg_color = "rgba(124,106,247,0.08)" if is_selected else "var(--surface2)"
            active_label = '<span style="font-family:DM Mono,monospace;font-size:0.6rem;color:#7c6af7;letter-spacing:0.08em"> ACTIVE</span>' if is_selected else ""
            st.markdown(f"""
            <div class="paper-card" style="border-color:{border_color};background:{bg_color};cursor:pointer">
                <div class="paper-title">{p['Title']}{active_label}</div>
                <div class="paper-meta">{p.get('PublicationDate','—')} &nbsp;{pill}</div>
                <div class="u-dots">
                    <div class="u-dot" style="background:{'#f0a654' if has_u1 else '#2a2a38'}"></div>
                    <div class="u-dot" style="background:{'#f06a6a' if has_u2 else '#2a2a38'}"></div>
                    <div class="u-dot" style="background:{'#a594f9' if has_u3 else '#2a2a38'}"></div>
                    <span class="u-label">U1 · U2 · U3</span>
                </div>
            </div>""", unsafe_allow_html=True)
            btn_label = f"Selected: {p['Title'][:30]}..." if is_selected else f"Focus on this paper"
            if st.button(btn_label, key=f"sel_{p['DOI']}", use_container_width=True):
                st.session_state.selected_doi = p["DOI"]
                st.session_state.suggestions = []
                with st.spinner("Generating suggestions for this paper..."):
                    try: st.session_state.suggestions = refresh_suggestions()
                    except: pass
                st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    if st.button("Clear database", use_container_width=True):
        db_clear(); st.session_state.suggestions = []; st.rerun()

    st.markdown("""
    <div style="font-size:0.62rem;color:#44445a;line-height:2.2;font-family:'DM Mono',monospace">
        <span style="color:#f0a654">●</span> U1 Conception &nbsp;
        <span style="color:#f06a6a">●</span> U2 Measurement &nbsp;
        <span style="color:#a594f9">●</span> U3 Analysis
    </div>""", unsafe_allow_html=True)

# ==============================================================================
# MAIN TABS
# ==============================================================================
tab_nav, tab_graph, tab_data = st.tabs([
    "Navigate", "Graph", "Data"
])

# ── NAVIGATE ──────────────────────────────────────────────────────────────────
with tab_nav:

    # Active paper banner
    sel_doi = st.session_state.get("selected_doi", "all")
    if sel_doi != "all":
        all_papers = db_papers()
        sel_paper = next((p for p in all_papers if p["DOI"] == sel_doi), None)
        if sel_paper:
            st.markdown(f"""
            <div style="background:rgba(124,106,247,0.1);border:1px solid rgba(124,106,247,0.35);
                        border-left:3px solid #7c6af7;border-radius:8px;padding:10px 16px;
                        margin-bottom:12px;display:flex;align-items:center;gap:12px">
                <div style="font-family:DM Mono,monospace;font-size:0.62rem;color:#7c6af7;
                            text-transform:uppercase;letter-spacing:0.1em;white-space:nowrap">Focused on</div>
                <div style="font-family:DM Sans,sans-serif;font-size:0.84rem;font-weight:500;
                            color:#a594f9;word-wrap:break-word;overflow-wrap:break-word">{sel_paper['Title']}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:rgba(45,212,160,0.06);border:1px solid rgba(45,212,160,0.2);
                    border-left:3px solid #2dd4a0;border-radius:8px;padding:8px 16px;
                    margin-bottom:12px;display:flex;align-items:center;gap:12px">
            <div style="font-family:DM Mono,monospace;font-size:0.62rem;color:#2dd4a0;
                        text-transform:uppercase;letter-spacing:0.1em">Scope</div>
            <div style="font-family:DM Sans,sans-serif;font-size:0.84rem;color:var(--muted)">
                All papers — select a paper in the sidebar to focus queries
            </div>
        </div>""", unsafe_allow_html=True)

    # Suggestions row
    if st.session_state.suggestions:
        sug_col, ref_col = st.columns([9, 1])
        with sug_col:
            st.markdown('<div class="section-label">Contextual suggestions from your papers</div>',
                        unsafe_allow_html=True)
        with ref_col:
            if st.button("Refresh", help="Refresh suggestions", use_container_width=True):
                with st.spinner("Thinking..."):
                    try: st.session_state.suggestions = refresh_suggestions()
                    except: pass
                st.rerun()

        cols = st.columns(len(st.session_state.suggestions))
        for i, (col, sug) in enumerate(zip(cols, st.session_state.suggestions)):
            with col:
                if st.button(sug, key=f"sug_btn_{i}", use_container_width=True):
                    db_add_message("me", sug)
                    with st.spinner("Querying graph..."):
                        ans, src = query_graph(sug)
                    db_add_message("rn", ans, src)
                    st.rerun()

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # Stakeholder queries — matched exactly to rubric requirements
    st.markdown('<div class="section-label">Required stakeholder queries</div>', unsafe_allow_html=True)
    sq1, sq2, sq3 = st.columns(3)

    def run_stakeholder(q, label):
        db_add_message("me", q)
        with st.spinner(f"Running {label}..."):
            ans, src = query_graph(q)
        db_add_message("rn", ans, src)
        st.rerun()

    with sq1:
        st.markdown("""<div class="stakeholder-card">
            <div class="stakeholder-icon">query_01 — Linkage</div>
            <div class="stakeholder-title">Find all fusion methods applied to Traffic Data and show their linked datasets</div>
        </div>""", unsafe_allow_html=True)
        if st.button("Run Linkage Query", key="sq1", use_container_width=True):
            run_stakeholder(
                "Linkage Query: Show me all fusion methods used for Traffic Data. "
                "For each method, list all datasets it is linked to via MethodKey. "
                "This demonstrates graph traversal — finding which methods connect to which datasets.",
                "linkage")

    with sq2:
        st.markdown("""<div class="stakeholder-card">
            <div class="stakeholder-icon">query_02 — Uncertainty</div>
            <div class="stakeholder-title">List all papers reporting U2 measurement uncertainty, grouped by sensor type</div>
        </div>""", unsafe_allow_html=True)
        if st.button("Run Uncertainty Query", key="sq2", use_container_width=True):
            run_stakeholder(
                "Uncertainty Query: List all papers that report U2 (Measurement) uncertainty. "
                "Group the results by sensor type or data type. "
                "Show the paper title, dataset name, sensor type, and the specific U2 uncertainty description.",
                "uncertainty")

    with sq3:
        st.markdown("""<div class="stakeholder-card">
            <div class="stakeholder-icon">query_03 — Discovery</div>
            <div class="stakeholder-title">Find the most popular dataset — most connections to different methods</div>
        </div>""", unsafe_allow_html=True)
        if st.button("Run Discovery Query", key="sq3", use_container_width=True):
            run_stakeholder(
                "Discovery Query: Which dataset in the knowledge graph has the most connections to different fusion methods? "
                "Rank all datasets by how many distinct methods they are linked to. "
                "This demonstrates aggregation across the graph.",
                "discovery")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # Chat
    messages = db_messages()
    if not messages:
        st.markdown("""
        <div class="welcome-box">
            <div class="welcome-title">Welcome to Fusion Lab</div>
            <div class="welcome-text">
                A knowledge graph navigator for data fusion research.<br>
                Ingest a paper using the sidebar, then ask questions grounded in your extracted data.
            </div>
            <div style="margin-top:12px">
                <div class="welcome-example">→ Show me all fusion methods used for Traffic Data</div>
                <div class="welcome-example">→ List papers with U2 uncertainty for Satellite Imagery</div>
                <div class="welcome-example">→ Which datasets are fused with Census Data?</div>
                <div class="welcome-example">→ What sensor types appear across loaded papers?</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in messages:
            if msg["role"] == "me":
                st.markdown(f'<div class="msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                body = msg["content"].replace("\n", "<br>")
                src  = f'<div class="msg-source">Source: {msg["source"]}</div>' if msg.get("source") else ""
                st.markdown(f'<div class="msg-rn">{body}{src}</div>', unsafe_allow_html=True)

    # Input
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    with st.form("qform", clear_on_submit=True):
        qc1, qc2 = st.columns([8, 1])
        with qc1:
            user_q = st.text_input("q", placeholder="Ask anything about your papers...",
                                   label_visibility="collapsed")
        with qc2:
            ask = st.form_submit_button("Ask", use_container_width=True)

    if ask and user_q:
        if not db_papers():
            st.warning("Ingest a paper first.")
        else:
            db_add_message("me", user_q)
            with st.spinner("Querying database..."):
                ans, src = query_graph(user_q)
            db_add_message("rn", ans, src)
            st.rerun()


# ── GRAPH ─────────────────────────────────────────────────────────────────────
with tab_graph:
    if not db_papers():
        st.markdown("""<div class="welcome-box">
            <div class="welcome-title">No data yet</div>
            <div class="welcome-text">Ingest papers using the sidebar to see the knowledge graph.</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div class="section-label">Force-directed knowledge graph - drag nodes - hover for details</div>""",
                    unsafe_allow_html=True)
        st.components.v1.html(build_graph_html(), height=640, scrolling=False)


# ── DATA ─────────────────────────────────────────────────────────────────────
with tab_data:
    papers   = db_papers()
    methods  = db_methods()
    datasets = db_datasets()

    if not papers:
        st.markdown("""<div class="welcome-box">
            <div class="welcome-title">No data yet</div>
            <div class="welcome-text">Ingest papers using the sidebar to see extracted data.</div>
        </div>""", unsafe_allow_html=True)
    else:
        # ── Top stats row ──
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px">
            <div style="background:var(--surface2);border:1px solid var(--border);border-radius:10px;padding:16px;text-align:center">
                <div style="font-family:Syne,sans-serif;font-size:2rem;font-weight:700;color:var(--green)">{len(papers)}</div>
                <div style="font-family:DM Mono,monospace;font-size:0.62rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em">Papers</div>
            </div>
            <div style="background:var(--surface2);border:1px solid var(--border);border-radius:10px;padding:16px;text-align:center">
                <div style="font-family:Syne,sans-serif;font-size:2rem;font-weight:700;color:var(--accent2)">{len(methods)}</div>
                <div style="font-family:DM Mono,monospace;font-size:0.62rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em">Fusion Methods</div>
            </div>
            <div style="background:var(--surface2);border:1px solid var(--border);border-radius:10px;padding:16px;text-align:center">
                <div style="font-family:Syne,sans-serif;font-size:2rem;font-weight:700;color:var(--amber)">{len(datasets)}</div>
                <div style="font-family:DM Mono,monospace;font-size:0.62rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em">Datasets</div>
            </div>
            <div style="background:var(--surface2);border:1px solid var(--border);border-radius:10px;padding:16px;text-align:center">
                <div style="font-family:Syne,sans-serif;font-size:2rem;font-weight:700;color:var(--red)">{db_count_u()}</div>
                <div style="font-family:DM Mono,monospace;font-size:0.62rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.1em">Uncertainty Tags</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Insights panel ──
        if methods and datasets:
            st.markdown('<div class="section-label">Knowledge graph insights</div>', unsafe_allow_html=True)

            # Most connected dataset
            from collections import Counter
            ds_method_counts = Counter(d["DataName"] for d in datasets if d["MethodKey"])
            top_dataset = ds_method_counts.most_common(1)

            # Fusion papers count
            fusion_count = sum(1 for p in papers if p.get("IsDataFusionPaper") == "Yes")

            # U2 coverage
            u2_count = sum(1 for d in datasets if d.get("U2"))
            u1_count = sum(1 for m in methods if m.get("U1"))
            u3_count = sum(1 for m in methods if m.get("U3"))

            # Data types
            dtypes = Counter(d["DataType"] for d in datasets if d.get("DataType"))
            top_dtype = dtypes.most_common(1)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="paper-card" style="margin-bottom:10px">
                    <div class="section-label">Fusion classification</div>
                    <div style="display:flex;gap:16px;margin-top:8px">
                        <div>
                            <div style="font-family:Syne,sans-serif;font-size:1.4rem;font-weight:700;color:var(--green)">{fusion_count}</div>
                            <div style="font-family:DM Mono,monospace;font-size:0.65rem;color:var(--muted)">Data fusion papers</div>
                        </div>
                        <div>
                            <div style="font-family:Syne,sans-serif;font-size:1.4rem;font-weight:700;color:var(--red)">{len(papers)-fusion_count}</div>
                            <div style="font-family:DM Mono,monospace;font-size:0.65rem;color:var(--muted)">Non-fusion papers</div>
                        </div>
                    </div>
                </div>
                <div class="paper-card">
                    <div class="section-label">Uncertainty coverage</div>
                    <div style="display:flex;gap:12px;margin-top:8px;flex-wrap:wrap">
                        <div style="background:rgba(240,166,84,0.1);border:1px solid rgba(240,166,84,0.25);border-radius:6px;padding:8px 12px;text-align:center">
                            <div style="font-family:Syne,sans-serif;font-size:1.2rem;font-weight:700;color:var(--amber)">{u1_count}</div>
                            <div style="font-family:DM Mono,monospace;font-size:0.6rem;color:var(--amber)">U1 Conception</div>
                        </div>
                        <div style="background:rgba(240,106,106,0.1);border:1px solid rgba(240,106,106,0.25);border-radius:6px;padding:8px 12px;text-align:center">
                            <div style="font-family:Syne,sans-serif;font-size:1.2rem;font-weight:700;color:var(--red)">{u2_count}</div>
                            <div style="font-family:DM Mono,monospace;font-size:0.6rem;color:var(--red)">U2 Measurement</div>
                        </div>
                        <div style="background:rgba(165,148,249,0.1);border:1px solid rgba(165,148,249,0.25);border-radius:6px;padding:8px 12px;text-align:center">
                            <div style="font-family:Syne,sans-serif;font-size:1.2rem;font-weight:700;color:var(--accent2)">{u3_count}</div>
                            <div style="font-family:DM Mono,monospace;font-size:0.6rem;color:var(--accent2)">U3 Analysis</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                top_ds_name = top_dataset[0][0] if top_dataset else "N/A"
                top_ds_count = top_dataset[0][1] if top_dataset else 0
                top_type = top_dtype[0][0] if top_dtype else "N/A"
                st.markdown(f"""
                <div class="paper-card" style="margin-bottom:10px">
                    <div class="section-label">Most connected dataset</div>
                    <div style="margin-top:8px">
                        <div style="font-family:Syne,sans-serif;font-size:1rem;font-weight:700;color:var(--amber);word-wrap:break-word">{top_ds_name}</div>
                        <div style="font-family:DM Mono,monospace;font-size:0.65rem;color:var(--muted);margin-top:4px">{top_ds_count} method connection(s)</div>
                    </div>
                </div>
                <div class="paper-card">
                    <div class="section-label">Most common data type</div>
                    <div style="margin-top:8px">
                        <div style="font-family:Syne,sans-serif;font-size:1rem;font-weight:700;color:var(--accent2);word-wrap:break-word">{top_type}</div>
                        <div style="font-family:DM Mono,monospace;font-size:0.65rem;color:var(--muted);margin-top:4px">{dtypes.get(top_type, 0)} dataset(s) of this type</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        # ── Downloads ──
        st.markdown('<div class="section-label">Download extracted data</div>', unsafe_allow_html=True)
        dc1, dc2, dc3 = st.columns(3)
        with dc1:
            st.download_button("Download DOI sheet",
                               data=to_csv(papers), file_name="DOI_sheet.csv",
                               mime="text/csv", use_container_width=True)
        with dc2:
            st.download_button("Download Fusion_Method sheet",
                               data=to_csv(methods), file_name="Fusion_Method_sheet.csv",
                               mime="text/csv", use_container_width=True)
        with dc3:
            st.download_button("Download Data sheet",
                               data=to_csv(datasets), file_name="Data_sheet.csv",
                               mime="text/csv", use_container_width=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        # ── Table viewer ──
        st.markdown('<div class="section-label">Browse database tables</div>', unsafe_allow_html=True)
        s1, s2, s3 = st.tabs(["Papers", "Fusion Methods", "Datasets"])
        with s1:
            st.markdown('<div class="section-label">papers table</div>', unsafe_allow_html=True)
            # Show clean subset of columns
            df = pd.DataFrame(papers)[["Title","Author","PublicationDate","FieldOfStudy","IsDataFusionPaper","DataFusionClassificationReason"]] if papers else pd.DataFrame()
            st.dataframe(df, use_container_width=True, hide_index=True)
        with s2:
            st.markdown('<div class="section-label">fusion_methods table</div>', unsafe_allow_html=True)
            df = pd.DataFrame(methods)[["MethodName","Description","U1","U3","OutputData"]] if methods else pd.DataFrame()
            st.dataframe(df, use_container_width=True, hide_index=True)
        with s3:
            st.markdown('<div class="section-label">datasets table</div>', unsafe_allow_html=True)
            df = pd.DataFrame(datasets)[["DataName","DataType","SensorType","SpatialCoverage","TemporalCoverage","U2","Provenance"]] if datasets else pd.DataFrame()
            st.dataframe(df, use_container_width=True, hide_index=True)
