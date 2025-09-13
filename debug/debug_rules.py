#!/usr/bin/env python3

from src.pysd.validation.rule_system import validation_registry

def debug_rules():
    """Debug what rules are registered."""
    registry = validation_registry
    
    print("=== VALIDATION REGISTRY DEBUG ===")
    print(f"Instance rules: {list(registry._instance_rules.keys())}")
    print(f"Container rules: {list(registry._container_rules.keys())}")
    print(f"Model rules: {list(registry._model_rules.keys())}")
    
    print("\n=== XTFIL RULES ===")
    print(f"XTFIL instance rules: {len(registry.get_instance_rules('XTFIL'))}")
    print(f"XTFIL container rules: {len(registry.get_container_rules('XTFIL'))}")
    print(f"XTFIL model rules: {len(registry.get_model_rules('XTFIL'))}")

if __name__ == "__main__":
    debug_rules()