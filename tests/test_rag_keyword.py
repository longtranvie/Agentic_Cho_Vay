from loan_agent.rag.ingest import _chunk_markdown
from loan_agent.rag.keyword_store import KeywordStore

DOCS = [
    {
        "source": "TT39",
        "dieu": "Điều 7",
        "snippet": "Điều kiện vay vốn: khách hàng có năng lực pháp luật dân sự.",
    },
    {
        "source": "TT39",
        "dieu": "Điều 8",
        "snippet": "Những nhu cầu vốn không được cho vay theo quy định.",
    },
]


def test_retrieve_returns_most_relevant():
    store = KeywordStore(DOCS)
    res = store.retrieve("điều kiện vay vốn", k=1)
    assert len(res) == 1
    assert res[0].dieu == "Điều 7"


def test_retrieve_empty_when_no_overlap():
    store = KeywordStore(DOCS)
    assert store.retrieve("xyz khong lien quan zzz", k=3) == []


def test_chunk_markdown_splits_by_dieu():
    md = "# TT39\n\n## Điều 7\nĐiều kiện vay vốn.\n\n## Điều 8\nKhông được cho vay."
    chunks = _chunk_markdown(md, "tt39")
    dieu_list = [c["dieu"] for c in chunks]
    assert "Điều 7" in dieu_list and "Điều 8" in dieu_list
