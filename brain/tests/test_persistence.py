
import pytest
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add brain root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.db import get_connection, init_db
from core.memory_service import memory_service
from core.vector_store import VectorStore

TEST_DB = "test_data/sentient_test.db"
TEST_INDEX = "test_data/faiss_test.index"

@pytest.fixture
def mock_db():
    # Setup test DB
    import core.db
    core.db.DB_PATH = Path(TEST_DB)
    init_db()
    yield
    # Cleanup
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    if os.path.exists(TEST_DB + "-journal"):
        os.remove(TEST_DB + "-journal")

@pytest.fixture
def mock_vector_store():
    # Setup test Vector Store
    import core.vector_store
    core.vector_store.DATA_DIR = Path("test_data")
    core.vector_store.INDEX_PATH = core.vector_store.DATA_DIR / "faiss_test.index"
    core.vector_store.META_PATH = core.vector_store.DATA_DIR / "faiss_meta_test.json"
    
    # Mock embedding generation to avoid loading heavy models
    with patch("core.vector_store.local_engine") as mock_engine:
        mock_engine.embed.return_value = [0.1] * 384
        vs = VectorStore()
        yield vs
    
    # Cleanup
    import shutil
    if os.path.exists("test_data"):
        shutil.rmtree("test_data")

def test_db_persistence(mock_db):
    memory_service._cache.clear()
    
    user = "test_user_1"
    memory_service.add_message(user, "user", "Hello World")
    
    # Check Cache
    assert len(memory_service._cache[user]) == 1
    assert memory_service._cache[user][0]["content"] == "Hello World"
    
    # Check DB
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT text FROM conversations WHERE user_id = ?", (user,))
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None
    assert row[0] == "Hello World"

def test_vector_store_add_search(mock_vector_store):
    vs = mock_vector_store
    
    vs.add("This is a memory", {"id": "1"})
    vs.add("Another memory", {"id": "2"})
    
    results = vs.search("memory", k=1)
    
    assert len(results) == 1
    # Since we mocked embeddings to be identical, search might return either, 
    # but functionally the pipeline runs.
    assert "id" in results[0]

