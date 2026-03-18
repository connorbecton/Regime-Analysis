"""
Quick test script to verify backend API is working
Run this before deploying to catch any issues
"""
import sys
import json

def test_imports():
    """Test that all required packages can be imported"""
    print("Testing imports...")
    try:
        import fastapi
        print("✓ FastAPI")
        import yfinance
        print("✓ yfinance")
        import pandas
        print("✓ pandas")
        import numpy
        print("✓ numpy")
        from pydantic import BaseModel
        print("✓ pydantic")
        print("\n✅ All imports successful!\n")
        return True
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Run: pip install -r api/requirements.txt")
        return False

def test_config():
    """Test config model"""
    print("Testing config model...")
    try:
        # Add api directory to path
        sys.path.insert(0, 'api')
        from main import ModelConfig
        
        config = ModelConfig(
            weight_defcyc=2.0,
            threshold_defensive=7.0,
            threshold_riskon=-7.0,
            ewma_span=6
        )
        print(f"✓ Config created: threshold=±{config.threshold_defensive}")
        print("\n✅ Config model works!\n")
        return True
    except Exception as e:
        print(f"\n❌ Config error: {e}")
        return False

def test_data_fetch():
    """Test data fetching from Yahoo Finance"""
    print("Testing data fetch...")
    try:
        sys.path.insert(0, 'api')
        from main import fetch_price_data
        
        # Fetch small amount of data
        tickers = ['SPY', 'XLF']
        data = fetch_price_data(tickers, '2025-01-01', '2025-03-01')
        
        print(f"✓ Fetched {len(data)} weeks of data")
        print(f"✓ Tickers: {list(data.columns)}")
        print("\n✅ Data fetch works!\n")
        return True
    except Exception as e:
        print(f"\n❌ Data fetch error: {e}")
        print("This might be a network issue or Yahoo Finance rate limit")
        return False

def test_signals():
    """Test signal calculation"""
    print("Testing signal calculation...")
    try:
        sys.path.insert(0, 'api')
        from main import fetch_price_data, calculate_signals, ModelConfig
        
        config = ModelConfig()
        
        # Fetch data
        tickers = ['XLU', 'XLP', 'XLV', 'XLF', 'XLI', 'XLB', 
                   'RPV', 'RPG', 'VYM', 'SPY', 'VSCH', 'HYG']
        data = fetch_price_data(tickers, '2024-01-01', '2026-03-01')
        
        # Calculate signals
        signals = calculate_signals(data, config)
        
        latest = signals.iloc[-1]
        print(f"✓ Signals calculated")
        print(f"✓ Latest regime: {latest['Regime']}")
        print(f"✓ EWMA score: {latest['EWMA_Score']:.2f}")
        print("\n✅ Signal calculation works!\n")
        return True
    except Exception as e:
        print(f"\n❌ Signal calculation error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("BACKEND API TEST SUITE")
    print("=" * 60)
    print()
    
    tests = [
        ("Imports", test_imports),
        ("Config Model", test_config),
        ("Data Fetch", test_data_fetch),
        ("Signal Calculation", test_signals)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"{'=' * 60}")
        print(f"TEST: {name}")
        print(f"{'=' * 60}")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results.append((name, False))
        print()
    
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(result for _, result in results)
    print()
    if all_passed:
        print("🎉 All tests passed! Backend is ready for deployment.")
    else:
        print("⚠️  Some tests failed. Fix issues before deploying.")
    
    sys.exit(0 if all_passed else 1)
