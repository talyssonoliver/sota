import pytest
import logging

@pytest.fixture(autouse=True)
def set_log_level():
    logging.getLogger().setLevel(logging.WARNING)
    # Silence most noisy loggers
    for name in [
        "dotenv.main", "httpx", "chromadb", "MemoryEngine"
    ]:
        logging.getLogger(name).setLevel(logging.ERROR)

    # Optionally, patch print to silence print statements in test mode
    import builtins, os
    if os.environ.get("TESTING", "0") == "1":
        builtins.print = lambda *a, **k: None
