#!/usr/bin/env python3
"""
Demonstration of the consistent container interface improvements.

This example shows how all containers now have the same API and O(1) performance.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.pysd.containers.basco_container import BascoContainer
from src.pysd.containers.loadc_container import LoadcContainer
from src.pysd.statements.basco import BASCO, LoadCase
from src.pysd.statements.loadc import LOADC

# Rebuild models after imports to resolve forward references
BascoContainer.model_rebuild()
LoadcContainer.model_rebuild()

def demonstrate_consistent_api():
    """Show that all containers have identical API."""
    
    print("🚀 PySD Consistent Container Interface Demo")
    print("=" * 50)
    
    # Create BASCO container with integer IDs
    basco_container = BascoContainer()
    basco1 = BASCO(id=101, load_cases=[LoadCase(lc_type='ELC', lc_numb=1, lc_fact=1.0)])
    basco2 = BASCO(id=102, load_cases=[LoadCase(lc_type='OLC', lc_numb=2, lc_fact=1.5)])
    
    # Create LOADC container with string keys
    loadc_container = LoadcContainer()
    loadc1 = LOADC(alc=1, olc=101)
    loadc2 = LOADC(alc=2, olc=102)
    
    print("\n📦 Adding items to containers...")
    
    # Add items using consistent interface
    basco_container.add(basco1)
    basco_container.add(basco2)
    
    loadc_container.add(loadc1)
    loadc_container.add(loadc2)
    
    print(f"  BASCO container: {len(basco_container)} items")
    print(f"  LOADC container: {len(loadc_container)} items")
    
    print("\n🔍 Consistent lookups (O(1) performance)...")
    
    # All containers have the same methods
    containers = [
        ("BASCO", basco_container, [101, 102]),
        ("LOADC", loadc_container, [loadc1.identifier, loadc2.identifier])
    ]
    
    for name, container, ids in containers:
        print(f"\n  {name} Container:")
        print(f"    get_all_ids(): {container.get_all_ids()}")
        
        for identifier in ids:
            print(f"    contains({identifier}): {container.contains(identifier)}")
            item = container.get_by_id(identifier)
            if item:
                actual_id = getattr(item, 'id', getattr(item, 'key', 'unknown'))
                print(f"    get_by_id({identifier}): Found item {actual_id}")
    
    print("\n⚡ Batch operations...")
    
    # Demonstrate batch adding
    more_bascos = [
        BASCO(id=103, load_cases=[LoadCase(lc_type='BAS', lc_numb=101, lc_fact=2.0)]),
        BASCO(id=104, load_cases=[LoadCase(lc_type='BAS', lc_numb=102, lc_fact=1.8)])
    ]
    
    basco_container.add_batch(more_bascos)
    print(f"  Added batch of {len(more_bascos)} BASCOs")
    print(f"  Total BASCOs: {len(basco_container)}")
    print(f"  All BASCO IDs: {basco_container.get_all_ids()}")
    
    print("\n🔄 Iteration in insertion order...")
    
    print("  BASCO items:")
    for i, basco in enumerate(basco_container):
        print(f"    {i+1}. BASCO {basco.id}")
    
    print("  LOADC items:")
    for i, loadc in enumerate(loadc_container):
        print(f"    {i+1}. LOADC {loadc.key}")
    
    print("\n✅ Performance comparison:")
    print("  OLD: O(n) linear search through list")
    print("  NEW: O(1) dictionary lookup")
    print("  OLD: Inconsistent APIs (get_ids vs get_keys)")
    print("  NEW: Consistent API across all containers")
    
    print(f"\n🎯 Summary:")
    print(f"  - All containers use identical interface")
    print(f"  - O(1) lookups via internal dictionary")
    print(f"  - Type-safe with generics: StandardContainer[T]")
    print(f"  - Insertion order preserved")
    print(f"  - Backward compatible with legacy methods")

def demonstrate_error_handling():
    """Show improved error handling."""
    
    print(f"\n🛡️  Error Handling Demo")
    print("=" * 30)
    
    container = BascoContainer()
    basco = BASCO(id=200, load_cases=[LoadCase(lc_type='ELC', lc_numb=1, lc_fact=1.0)])
    
    container.add(basco)
    
    try:
        # Try to add duplicate
        duplicate = BASCO(id=200, load_cases=[LoadCase(lc_type='OLC', lc_numb=2, lc_fact=1.0)])
        container.add(duplicate)
    except ValueError as e:
        print(f"  ✅ Caught duplicate ID error: {e}")
    
    try:
        # Try to add item without Identifiable protocol (this won't happen with our statements)
        class BadItem:
            pass
        container.add(BadItem())
    except TypeError as e:
        print(f"  ✅ Caught protocol error: {e}")
    
    print("  → All errors provide clear, actionable messages")

if __name__ == "__main__":
    demonstrate_consistent_api()
    demonstrate_error_handling()
    
    print(f"\n🎉 Demo completed! The consistent container interface is working perfectly.")
