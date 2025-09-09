"""
Example demonstrating different validation modes in PySD.

This script shows how to use various validation levels to control
error handling behavior during model creation.
"""

from src.pysd.statements import RFILE, FILST, LOADC
from src.pysd.sdmodel import SD_BASE
from src.pysd.validation import (
    set_validation_mode, get_validation_mode, ValidationMode, 
    permissive_validation, no_validation, strict_validation
)


def demo_validation_modes():
    """Demonstrate different validation mode behaviors."""
    
    print("=== PySD Validation Mode Demonstration ===\n")
    
    # Show current default mode
    print(f"🔧 Default validation mode: {get_validation_mode()}")
    
    # ===== Mode 1: STRICT Validation =====
    print("\n📋 1. STRICT MODE - Catches all issues")
    set_validation_mode(ValidationMode.STRICT)
    
    try:
        with SD_BASE.create_writer("test_strict.inp") as model:
            # This will create warnings for multiple FILST entries
            model.add(FILST(name="project1", vers="1.0"))
            model.add(FILST(name="project1", vers="2.0"))  # Duplicate name
            print("   ✅ STRICT mode: Model created successfully")
    except Exception as e:
        print(f"   ⚠️  STRICT mode caught: {type(e).__name__}: {e}")
    
    # ===== Mode 2: NORMAL Validation =====
    print("\n📋 2. NORMAL MODE - Only errors raise exceptions")
    set_validation_mode(ValidationMode.NORMAL)
    
    try:
        with SD_BASE.create_writer("test_normal.inp") as model:
            model.add(FILST(name="project1", vers="1.0"))
            model.add(FILST(name="project1", vers="2.0"))  # Duplicate name warning
            print("   ✅ NORMAL mode: Model created (warnings logged)")
    except Exception as e:
        print(f"   ❌ NORMAL mode caught: {type(e).__name__}: {e}")
    
    # ===== Mode 3: PERMISSIVE Validation =====
    print("\n📋 3. PERMISSIVE MODE - Very lenient")
    set_validation_mode(ValidationMode.PERMISSIVE)
    
    try:
        with SD_BASE.create_writer("test_permissive.inp") as model:
            model.add(FILST(name="project1", vers="1.0"))
            model.add(FILST(name="project1", vers="2.0"))
            # Even more validation issues would be tolerated
            print("   ✅ PERMISSIVE mode: Model created (most issues ignored)")
    except Exception as e:
        print(f"   ❌ PERMISSIVE mode caught: {type(e).__name__}: {e}")
    
    # ===== Mode 4: DISABLED Validation =====
    print("\n📋 4. DISABLED MODE - No validation exceptions")
    set_validation_mode(ValidationMode.DISABLED)
    
    try:
        with SD_BASE.create_writer("test_disabled.inp") as model:
            model.add(FILST(name="project1", vers="1.0"))
            model.add(FILST(name="project1", vers="2.0"))
            print("   ✅ DISABLED mode: Model created (no validation)")
    except Exception as e:
        print(f"   ❌ DISABLED mode caught: {type(e).__name__}: {e}")


def demo_context_managers():
    """Demonstrate validation context managers."""
    
    print("\n\n=== Context Manager Demonstration ===\n")
    
    # Reset to normal mode
    set_validation_mode(ValidationMode.NORMAL)
    
    with SD_BASE.create_writer("test_context.inp") as model:
        
        # Normal validation for basic components
        print("📋 Using default NORMAL mode for basic components")
        model.add(FILST(name="main_project", vers="1.0"))
        model.add(RFILE(fnm="R1", suf="SIN"))
        
        # Strict validation for critical components
        print("📋 Using STRICT mode for critical load components")
        with strict_validation():
            try:
                # This should work fine
                model.add(LOADC(run_number=1, alc=(1, 6), olc=(101, 106)))
                print("   ✅ Critical component added successfully")
            except Exception as e:
                print(f"   ❌ Critical validation failed: {e}")
        
        # Permissive validation for experimental features
        print("📋 Using PERMISSIVE mode for experimental features")
        with permissive_validation():
            # Add potentially problematic items (but within field limits)
            model.add(FILST(name="experim", vers="0.1-beta"))  # Fixed length
            print("   ✅ Experimental features added")
        
        # No validation for bulk imports
        print("📋 Using NO VALIDATION for bulk import")
        with no_validation():
            # Bulk add without validation overhead
            bulk_items = [
                FILST(name="bulk1", vers="1.0"),
                FILST(name="bulk2", vers="1.0"),
                FILST(name="bulk3", vers="1.0"),
            ]
            model.add(bulk_items)
            print("   ✅ Bulk items added without validation")
        
        # Check final model status
        summary = model.get_validation_summary()
        print(f"\n📊 Final model summary:")
        print(f"   Total items: {summary['total_items']}")
        print(f"   Has warnings: {summary['has_warnings']}")
        print(f"   Has errors: {summary['has_errors']}")


def demo_rule_specific_control():
    """Demonstrate fine-grained rule control."""
    
    print("\n\n=== Rule-Specific Control Demonstration ===\n")
    
    from src.pysd.validation import disable_validation_rule, enable_validation_rule
    
    # Reset to normal mode
    set_validation_mode(ValidationMode.NORMAL)
    
    # Disable specific warning rules
    print("📋 Disabling duplicate name warnings")
    disable_validation_rule("FILST_DUPLICATE_NAME_WARNING")
    
    with SD_BASE.create_writer("test_rules.inp") as model:
        # This should not generate warnings now
        model.add(FILST(name="same_name", vers="1.0"))
        model.add(FILST(name="same_name", vers="2.0"))
        print("   ✅ Duplicate names added without warnings")
        
        summary = model.get_validation_summary()
        print(f"   Has warnings: {summary['has_warnings']}")
    
    # Re-enable the rule
    print("📋 Re-enabling duplicate name warnings")
    enable_validation_rule("FILST_DUPLICATE_NAME_WARNING")


def main():
    """Main demonstration function."""
    try:
        demo_validation_modes()
        demo_context_managers()
        demo_rule_specific_control()
        
        print("\n🎉 Validation demonstration completed successfully!")
        print("\n💡 Key Takeaways:")
        print("   • Use ValidationMode.NORMAL for most applications")
        print("   • Use ValidationMode.STRICT during development/testing")
        print("   • Use ValidationMode.PERMISSIVE for legacy data import")
        print("   • Use context managers for temporary validation changes")
        print("   • Use rule-specific controls for fine-grained behavior")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()