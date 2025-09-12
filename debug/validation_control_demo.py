"""
Demo script showing selective validation control - Scenario 4 implementation.

This demonstrates how to build partial models (like just BASCO containers) 
without validation errors, then enable full validation when ready.
"""

from src.pysd.sdmodel import SD_BASE
from src.pysd.statements import BASCO, GRECO
from src.pysd.statements.basco import LoadCase

def demo_scenario_4_selective_validation():
    """
    Demo Scenario 4: Selective validation control for testing and partial model building
    """
    
    print("=== Validation Control Demo - Scenario 4 ===\n")
    
    # Create a model with normal validation settings
    sd_model = SD_BASE()
    
    print("1. Building BASCO container first (may have forward references to GRECO)")
    
    # Disable cross-container validation temporarily
    sd_model.disable_cross_container_validation()
    print("   ✓ Cross-container validation disabled")
    
    # Add BASCO items that reference GRECO items that don't exist yet
    basco1 = BASCO(
        id=1,
        load_cases=[
            LoadCase(lc_type='ELC', lc_numb=1, lc_fact=1.0)
        ],
        gre="A"  # References GRECO A that doesn't exist yet
    )
    
    basco2 = BASCO(
        id=2,
        load_cases=[
            LoadCase(lc_type='OLC', lc_numb=2, lc_fact=1.2)
        ],
        gre="B"  # References GRECO B that doesn't exist yet
    )
    
    # These additions won't fail even though GRECO A and B don't exist
    sd_model.add([basco1, basco2])
    print(f"   ✓ Added {len(sd_model.basco)} BASCO items with forward GRECO references")
    
    print("\n2. Container validation is still working for duplicates")
    
    # Try adding duplicate BASCO (this should still be caught)
    try:
        duplicate_basco = BASCO(
            id=1,  # Same ID as basco1
            load_cases=[LoadCase(lc_type='ELC', lc_numb=3, lc_fact=1.0)]
        )
        sd_model.add(duplicate_basco)
        print("   ❌ ERROR: Duplicate should have been caught!")
    except ValueError as e:
        print(f"   ✓ Container validation caught duplicate: {str(e)[:80]}...")
    
    print("\n3. Adding GRECO items that BASCO references")
    
    # Add the referenced GRECO items
    greco_a = GRECO(id="A", hei=10.0, wid=5.0, tos=2.0, bot=1.0)
    greco_b = GRECO(id="B", hei=12.0, wid=6.0, tos=2.5, bot=1.5)
    
    sd_model.add([greco_a, greco_b])
    print(f"   ✓ Added {len(sd_model.greco)} GRECO items")
    
    print("\n4. Re-enabling cross-container validation for final check")
    
    # Re-enable cross-container validation
    sd_model.enable_cross_container_validation()
    print("   ✓ Cross-container validation re-enabled")
    
    # Now run a final validation - should pass since all references are resolved
    try:
        sd_model._validate_cross_references()
        print("   ✅ Final cross-container validation passed!")
    except ValueError as e:
        print(f"   ❌ Final validation failed: {e}")
    
    print(f"\n5. Model summary:")
    print(f"   - GRECO items: {len(sd_model.greco)}")
    print(f"   - BASCO items: {len(sd_model.basco)}")
    print(f"   - Total items: {len(sd_model.all_items)}")
    
    return sd_model

def demo_context_managers():
    """
    Demo using context managers for temporary validation control
    """
    
    print("\n=== Context Manager Demo ===\n")
    
    sd_model = SD_BASE()
    
    print("1. Using context manager to temporarily disable cross-validation")
    
    with sd_model.cross_validation_disabled():
        print("   ✓ Inside context - cross validation disabled")
        
        # Add items with forward references
        basco = BASCO(
            id=10,
            load_cases=[LoadCase(lc_type='ELC', lc_numb=5, lc_fact=1.0)],
            gre="C"
        )
        sd_model.add(basco)
        print("   ✓ Added BASCO with forward reference to GRECO C")
    
    print("   ✓ Outside context - cross validation re-enabled automatically")
    
    print("\n2. Using context manager to disable container validation")
    
    with sd_model.container_validation_disabled():
        print("   ✓ Inside context - container validation disabled")
        
        # Manually set parent references (in case they weren't set yet)
        for container_name in ['basco', 'greco', 'loadc']:
            container = getattr(sd_model, container_name)
            if hasattr(container, 'set_parent_model'):
                container.set_parent_model(sd_model)
        
        # Add duplicate IDs (normally would fail)
        basco_dup1 = BASCO(
            id=99,
            load_cases=[LoadCase(lc_type='ELC', lc_numb=6, lc_fact=1.0)]
        )
        basco_dup2 = BASCO(
            id=99,  # Same ID
            load_cases=[LoadCase(lc_type='OLC', lc_numb=7, lc_fact=1.1)]
        )
        
        sd_model.add([basco_dup1, basco_dup2])
        print("   ✓ Added BASCO items with duplicate IDs (normally would fail)")
    
    print("   ✓ Outside context - container validation re-enabled automatically")
    
    print(f"\n   Final BASCO count: {len(sd_model.basco)} (includes duplicates)")

def demo_method_control():
    """
    Demo using direct method calls for validation control
    """
    
    print("\n=== Method Control Demo ===\n")
    
    sd_model = SD_BASE()
    
    print("1. Method-based validation control")
    print(f"   - Container validation: {sd_model.container_validation_enabled}")
    print(f"   - Cross-container validation: {sd_model.cross_container_validation_enabled}")
    
    # Disable container validation
    sd_model.disable_container_validation()
    print("\n   ✓ Container validation disabled")
    print(f"   - Container validation: {sd_model.container_validation_enabled}")
    print(f"   - Cross-container validation: {sd_model.cross_container_validation_enabled}")
    
    # Disable cross validation
    sd_model.disable_cross_container_validation()
    print("\n   ✓ Cross-container validation disabled")
    print(f"   - Container validation: {sd_model.container_validation_enabled}")
    print(f"   - Cross-container validation: {sd_model.cross_container_validation_enabled}")
    
    # Re-enable both
    sd_model.enable_container_validation()
    sd_model.enable_cross_container_validation()
    print("\n   ✓ Both validations re-enabled")
    print(f"   - Container validation: {sd_model.container_validation_enabled}")
    print(f"   - Cross-container validation: {sd_model.cross_container_validation_enabled}")

if __name__ == "__main__":
    # Run the demos
    model = demo_scenario_4_selective_validation()
    demo_context_managers()
    demo_method_control()
    
    print("\n🎯 Demo complete! Scenario 4 selective validation is working perfectly.")
    print("\nKey benefits:")
    print("✅ Build partial models without cross-reference errors")
    print("✅ Container validation still catches duplicates")
    print("✅ Context managers for temporary control")
    print("✅ Method-based control for fine-grained management")
    print("✅ Perfect for testing individual containers")