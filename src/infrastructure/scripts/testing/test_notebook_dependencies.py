#!/usr/bin/env python3
"""
Test script to validate the Docker Security Analysis notebook dependencies
"""


def test_imports():
    """Test all required imports for the notebook"""
    print("🧪 Testing Docker Security Analysis Notebook Dependencies")
    print("=" * 60)

    try:
        import pandas as pd

        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False

    try:
        import numpy as np

        print("✅ numpy imported successfully")
    except ImportError as e:
        print(f"❌ numpy import failed: {e}")
        return False

    try:
        import matplotlib.pyplot as plt

        print("✅ matplotlib imported successfully")
    except ImportError as e:
        print(f"❌ matplotlib import failed: {e}")
        return False

    try:
        import seaborn as sns

        print("✅ seaborn imported successfully")
    except ImportError as e:
        print(f"❌ seaborn import failed: {e}")
        return False

    try:
        import plotly

        print(f"✅ plotly imported successfully (version: {plotly.__version__})")
    except ImportError as e:
        print(f"❌ plotly import failed: {e}")
        return False

    return True


def test_basic_functionality():
    """Test basic functionality that the notebook uses"""
    print("\n🔧 Testing Basic Functionality")
    print("=" * 40)

    try:
        import pandas as pd

        # Test DataFrame creation (used in notebook)
        test_data = [
            {
                "filename": "test.dockerfile",
                "type": "vulnerability",
                "severity": 4,
            }
        ]
        df = pd.DataFrame(test_data)
        print(f"✅ DataFrame creation works: {len(df)} rows")

        # Test basic operations
        df["test_col"] = df["filename"].str.extract(r"([^.]+)")
        print("✅ String extraction works")

        # Test groupby (used in notebook)
        grouped = df.groupby("type").size()
        print("✅ DataFrame groupby works")

        return True

    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


def main():
    """Main test function"""
    print("🛡️ Docker Security Analysis Notebook - Dependency Test")
    print("=" * 70)

    imports_ok = test_imports()
    functionality_ok = test_basic_functionality()

    print("\n" + "=" * 70)
    print("📊 TEST RESULTS")
    print("=" * 70)

    if imports_ok and functionality_ok:
        print("🎉 ALL TESTS PASSED!")
        print("✅ The notebook should work without import errors")
        print("✅ All visualization libraries are available")
        print("✅ Ready to run docker_security_analysis.ipynb")
    else:
        print("⚠️ SOME TESTS FAILED")
        if not imports_ok:
            print("❌ Import issues detected")
            print("💡 Try: pip install pandas matplotlib seaborn plotly numpy")
        if not functionality_ok:
            print("❌ Functionality issues detected")

    print("\n🔍 To run the notebook:")
    print("1. Open docker_security_analysis.ipynb in VS Code")
    print("2. Select Python kernel")
    print("3. Run all cells")


if __name__ == "__main__":
    main()
