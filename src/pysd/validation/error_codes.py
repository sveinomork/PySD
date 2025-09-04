"""
Standardized error codes for validation.
"""

class ErrorCodes:
    """Standardized error codes for different validation types."""
    
    # Format: {STATEMENT}-{CATEGORY}-{NUMBER}
    
    # GRECO validation errors
    GRECO_ID_INVALID = "GRECO-ID-001"
    GRECO_BAS_COUNT_INVALID = "GRECO-BAS-001"
    GRECO_ELC_REFERENCE_INVALID = "GRECO-ELC-001"
    GRECO_DUPLICATE_ID = "GRECO-CONTAINER-001"
    
    @classmethod
    def get_description(cls, code: str) -> str:
        """Get human-readable description for error code."""
        descriptions = {
            cls.GRECO_ID_INVALID: "GRECO ID must be a single uppercase letter A-Z",
            cls.GRECO_BAS_COUNT_INVALID: "GRECO must have exactly 6 BAS (one per load resultant: Fx, Fy, Fz, Mx, My, Mz)",
            cls.GRECO_ELC_REFERENCE_INVALID: "GRECO ELC must be defined as OLC in LOADC",
            cls.GRECO_DUPLICATE_ID: "GRECO ID already exists in container",
        }
        return descriptions.get(code, "Unknown error")