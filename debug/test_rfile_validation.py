"""
Test script to demonstrate RFILE file existence validation across different validation modes.
"""

from src.pysd.statements import RFILE, FILST
from src.pysd.sdmodel import SD_BASE
from src.pysd.validation import set_validation_mode, ValidationMode

def test_file_existence_validation():
    """Test RFILE file existence validation in different modes."""
    
    print("=== RFILE File Existence Validation Test ===\n")
    
    # Test with STRICT mode
    print("📋 Testing with STRICT validation mode:")
    set_validation_mode(ValidationMode.STRICT)
    try:
        rfile = RFILE(
            pre=r"C:\Users\nx74\Work\ShellDesign1\AquaPod_09\Analyse_file",
            fnm="R1",
            suf="SIN",
            typ="SHE"
        )
        print("   ✅ STRICT mode: RFILE created (file exists)")
    except Exception as e:
        print(f"   ❌ STRICT mode caught error: {type(e).__name__}")
        print(f"      Error: {str(e)[:100]}...")
    
    # Test with NORMAL mode  
    print("\n📋 Testing with NORMAL validation mode:")
    set_validation_mode(ValidationMode.NORMAL)
    try:
        rfile = RFILE(
            pre=r"C:\Users\nx74\Work\ShellDesign1\AquaPod_09\Analyse_file",
            fnm="R1", 
            suf="SIN",
            typ="SHE"
        )
        print("   ✅ NORMAL mode: RFILE created (file exists)")
    except Exception as e:
        print(f"   ❌ NORMAL mode caught error: {type(e).__name__}")
        print(f"      Error: {str(e)[:100]}...")
    
    # Test with PERMISSIVE mode
    print("\n📋 Testing with PERMISSIVE validation mode:")
    set_validation_mode(ValidationMode.PERMISSIVE)
    try:
        rfile = RFILE(
            pre=r"C:\Users\nx74\Work\ShellDesign1\AquaPod_09\Analyse_file",
            fnm="R1",
            suf="SIN", 
            typ="SHE"
        )
        print("   ✅ PERMISSIVE mode: RFILE created (file exists)")
    except Exception as e:
        print(f"   ❌ PERMISSIVE mode caught error: {type(e).__name__}")
        print(f"      Error: {str(e)[:100]}...")
    
    # Test with DISABLED mode
    print("\n📋 Testing with DISABLED validation mode:")
    set_validation_mode(ValidationMode.DISABLED)
    try:
        rfile = RFILE(
            pre=r"C:\Users\nx74\Work\ShellDesign1\AquaPod_09\Analyse_file", 
            fnm="R1",
            suf="SIN",
            typ="SHE"
        )
        print("   ✅ DISABLED mode: RFILE created (file exists)")
    except Exception as e:
        print(f"   ❌ DISABLED mode caught error: {type(e).__name__}")
        print(f"      Error: {str(e)[:100]}...")

    # Test with an existing file (should work in all modes)
    print("\n📋 Testing with existing file (should work in all modes):")
    set_validation_mode(ValidationMode.STRICT)
    try:
        # Create a temporary test file
        import tempfile
        import os
        
        # Create a temporary directory and file
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test.SIN")
            with open(test_file, 'w') as f:
                f.write("# Test file")
            
            rfile_valid = RFILE(
                pre=temp_dir,
                fnm="test",
                suf="SIN",
                typ="SHE"
            )
            print(f"   ✅ Valid file path: RFILE created successfully")
            print(f"      Path: {temp_dir}\\test.SIN")
            
    except Exception as e:
        print(f"   ❌ Valid file test failed: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_file_existence_validation()