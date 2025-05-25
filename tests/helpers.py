import os
import shutil

def setup_test_directories():
    """Create necessary test directories and files for retrieval QA tests."""
    dirs = [
        os.path.join(os.path.dirname(__file__), "test_data"),
        os.path.join(os.path.dirname(__file__), "test_data", "context-store"),
        os.path.join(os.path.dirname(__file__), "..", "context-store"),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    content = "This is a test document about RLS rules in Supabase."
    files = [
        os.path.join(os.path.dirname(__file__), "test_data", "context-store", "test_doc.md"),
        os.path.join(os.path.dirname(__file__), "..", "context-store", "test_doc.md"),
    ]
    for f in files:
        with open(f, "w") as file:
            file.write(content)

def setup_test_files():
    """Create test directories and files needed for tests."""
    # Create directories in all relevant locations
    dirs = [
        os.path.join(os.path.dirname(__file__), "test_data"),
        os.path.join(os.path.dirname(__file__), "test_data", "context-store"),
        os.path.join(os.path.dirname(__file__), "..", "context-store"),
        os.path.join("test_data"),
        os.path.join("test_data", "context-store"),
        os.path.join("context-store"),
        os.path.join("tests", "test_data"),
        os.path.join("tests", "test_data", "context-store"),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    # Create test files with sample content in all relevant locations
    test_content = "This is a test document about RLS rules in Supabase."
    files = [
        os.path.join(os.path.dirname(__file__), "test_data", "context-store", "test_doc.md"),
        os.path.join(os.path.dirname(__file__), "..", "context-store", "test_doc.md"),
        os.path.join("test_data", "context-store", "test_doc.md"),
        os.path.join("context-store", "test_doc.md"),
        os.path.join("tests", "test_data", "context-store", "test_doc.md"),
    ]
    for f in files:
        with open(f, "w") as file:
            file.write(test_content)
    return files

def cleanup_test_files():
    """Remove all test files and directories created for tests."""
    paths = [
        os.path.join(os.path.dirname(__file__), "test_data"),
        os.path.join(os.path.dirname(__file__), "..", "context-store", "test_doc.md"),
        os.path.join("test_data"),
        os.path.join("context-store", "test_doc.md"),
        os.path.join("tests", "test_data"),
    ]
    for p in paths:
        if os.path.isfile(p):
            try:
                os.remove(p)
            except Exception:
                pass
        elif os.path.isdir(p):
            try:
                shutil.rmtree(p)
            except Exception:
                pass

outputs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")

def teardown_module(module):
    """Cleanup outputs directory after tests finish."""
    if os.path.exists(outputs_dir):
        for child in os.listdir(outputs_dir):
            child_path = os.path.join(outputs_dir, child)
            if os.path.isdir(child_path):
                shutil.rmtree(child_path)
            else:
                os.remove(child_path)
