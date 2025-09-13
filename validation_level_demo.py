"""
Demonstration of the new ValidationLevel enum-based API for PySD.

This script shows how to use the ValidationLevel enum for type-safe 
validation configuration instead of error-prone string values.
"""

from src.pysd.statements import DECAS, BASCO, LoadCase, LOADC
from src.pysd.sdmodel import SD_BASE
from src.pysd.validation.core import ValidationLevel

def demonstrate_validation_levels():
    """Demonstrate all validation levels with the enum API."""
    
    print("🎯 ValidationLevel Enum Demonstration")
    print("=" * 50)
    
    # Test ValidationLevel.DISABLED
    print(f"\n1️⃣  Testing ValidationLevel.DISABLED")
    model_disabled = SD_BASE(validation_level=ValidationLevel.DISABLED)
    print(f"   Validation level: {model_disabled.validation_level}")
    print(f"   Validation enabled: {model_disabled.validation_enabled}")
    
    # Should allow invalid references without error
    model_disabled.add(LOADC(run_number=1, alc=1, olc=110))
    invalid_decas = DECAS(ls='ULS', bas=999)  # 999 doesn't exist
    model_disabled.add(invalid_decas, validation=True)
    print(f"   ✅ Added invalid DECAS without error: {invalid_decas.input}")
    
    # Test ValidationLevel.NORMAL  
    print(f"\n2️⃣  Testing ValidationLevel.NORMAL")
    model_normal = SD_BASE(validation_level=ValidationLevel.NORMAL)
    print(f"   Validation level: {model_normal.validation_level}")
    print(f"   Cross-object validation: {model_normal.cross_object_validation}")
    
    # Add valid statements
    model_normal.add(LOADC(run_number=1, alc=1, olc=110))
    model_normal.add(BASCO(id=101, load_cases=[LoadCase(lc_type='OLC', lc_numb=110)]))
    valid_decas = DECAS(ls='ULS', bas=101)
    model_normal.add(valid_decas, validation=True)
    print(f"   ✅ Added valid DECAS with immediate validation: {valid_decas.input}")
    
    # Test ValidationLevel.STRICT
    print(f"\n3️⃣  Testing ValidationLevel.STRICT") 
    model_strict = SD_BASE(validation_level=ValidationLevel.STRICT)
    print(f"   Validation level: {model_strict.validation_level}")
    print(f"   All validation flags enabled: {model_strict.validation_enabled}")
    
    model_strict.add(LOADC(run_number=1, alc=1, olc=110))
    model_strict.add(BASCO(id=101, load_cases=[LoadCase(lc_type='OLC', lc_numb=110)]))
    strict_decas = DECAS(ls='ULS', bas=101)
    model_strict.add(strict_decas, validation=True)
    print(f"   ✅ Added valid DECAS with strict validation: {strict_decas.input}")
    
    # Test validation error catching
    print(f"\n4️⃣  Testing Validation Error Handling")
    try:
        error_decas = DECAS(ls='ULS', bas=888)  # 888 doesn't exist
        model_normal.add(error_decas, validation=True)
        print("   ❌ Expected validation error was not caught")
    except ValueError as e:
        print(f"   ✅ Validation error caught: {str(e)[:60]}...")
    
    print(f"\n5️⃣  Testing Type Safety")
    try:
        # This should cause a Pydantic ValidationError due to type mismatch
        SD_BASE(validation_level="invalid_string")
        print("   ❌ Expected type validation error was not caught")
    except Exception as e:
        print(f"   ✅ Type validation error caught: {type(e).__name__}")
        print(f"      Message: {str(e)[:60]}...")
    
    print(f"\n🎉 ValidationLevel enum demonstration completed!")
    print(f"   • Type-safe validation level configuration")
    print(f"   • Clear enum values: DISABLED, NORMAL, STRICT")
    print(f"   • Pydantic validation for type safety")
    print(f"   • Immediate validation feedback")

def show_api_comparison():
    """Show the improvement from string-based to enum-based API."""
    
    print(f"\n📊 API Comparison")
    print("=" * 50)
    
    print("❌ Old String-Based API (error-prone):")
    print("   model = SD_BASE(validation_level='normal')   # typos possible")
    print("   model = SD_BASE(validation_level='Normal')   # case sensitive")  
    print("   model = SD_BASE(validation_level='enabled')  # wrong values")
    
    print("\n✅ New Enum-Based API (type-safe):")
    print("   model = SD_BASE(validation_level=ValidationLevel.NORMAL)")
    print("   model = SD_BASE(validation_level=ValidationLevel.STRICT)")
    print("   model = SD_BASE(validation_level=ValidationLevel.DISABLED)")
    
    print(f"\n📋 Benefits of Enum API:")
    print(f"   • IDE autocompletion and type checking")
    print(f"   • No typos or case sensitivity issues") 
    print(f"   • Clear, self-documenting code")
    print(f"   • Runtime type validation by Pydantic")
    print(f"   • Better maintainability")

if __name__ == "__main__":
    demonstrate_validation_levels()
    show_api_comparison()