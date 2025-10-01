"""
Tests for validation utility functions.

Tests the reusable validation functions that are used across
different validation rule files.
"""

from src.pysd.validation.validation_utils import (
    check_duplicate_ids,
    check_id_range,
    check_positive_values,
    check_non_negative_values,
    check_label_length,
    check_material_reference,
    check_unused_definition,
)


# Mock classes for testing
class MockStatement:
    """Mock statement for testing."""

    def __init__(self, id, **kwargs):
        self.id = id
        for key, value in kwargs.items():
            setattr(self, key, value)


class MockContainer:
    """Mock container for testing."""

    def __init__(self, items):
        self.items = items

    def has_id(self, item_id):
        """Check if container has item with given ID."""
        return any(item.id == item_id for item in self.items)

    def contains(self, item_id):
        """Alternative method name for checking existence."""
        return self.has_id(item_id)


class MockModel:
    """Mock model for testing."""

    def __init__(self, **containers):
        for name, container in containers.items():
            setattr(self, name, container)


class TestCheckDuplicateIds:
    """Tests for check_duplicate_ids function."""

    def test_no_duplicates(self):
        """Test with unique IDs - should return no issues."""
        items = [MockStatement(1), MockStatement(2), MockStatement(3)]
        container = MockContainer(items)

        issues = check_duplicate_ids(container, "RETYP")

        assert len(issues) == 0

    def test_single_duplicate(self):
        """Test with one duplicate ID - should return one issue."""
        items = [MockStatement(1), MockStatement(2), MockStatement(1)]
        container = MockContainer(items)

        issues = check_duplicate_ids(container, "RETYP")

        assert len(issues) == 1
        assert issues[0].severity == "error"
        assert issues[0].code == "RETYP_DUPLICATE_ID"
        assert "Duplicate RETYP ID 1" in issues[0].message

    def test_multiple_duplicates(self):
        """Test with multiple duplicate IDs - should return multiple issues."""
        items = [
            MockStatement(1),
            MockStatement(2),
            MockStatement(1),
            MockStatement(3),
            MockStatement(2),
        ]
        container = MockContainer(items)

        issues = check_duplicate_ids(container, "SRTYP")

        assert len(issues) == 2
        assert all(issue.severity == "error" for issue in issues)
        assert all("SRTYP_DUPLICATE_ID" == issue.code for issue in issues)

    def test_empty_container(self):
        """Test with empty container - should return no issues."""
        container = MockContainer([])

        issues = check_duplicate_ids(container, "TETYP")

        assert len(issues) == 0

    def test_custom_error_code(self):
        """Test with custom error code suffix."""
        items = [MockStatement(1), MockStatement(1)]
        container = MockContainer(items)

        issues = check_duplicate_ids(container, "TEST", error_code_suffix="DUP_CHECK")

        assert len(issues) == 1
        assert issues[0].code == "TEST_DUP_CHECK"


class TestCheckIdRange:
    """Tests for check_id_range function."""

    def test_all_in_range(self):
        """Test with all IDs in valid range - should return no issues."""
        items = [MockStatement(1), MockStatement(50), MockStatement(100)]
        container = MockContainer(items)

        issues = check_id_range(container, "RETYP", 1, 100)

        assert len(issues) == 0

    def test_id_below_minimum(self):
        """Test with ID below minimum - should return issue."""
        items = [MockStatement(0), MockStatement(50)]
        container = MockContainer(items)

        issues = check_id_range(container, "RETYP", 1, 100)

        assert len(issues) == 1
        assert issues[0].severity == "error"
        assert "must be between 1 and 100" in issues[0].message

    def test_id_above_maximum(self):
        """Test with ID above maximum - should return issue."""
        items = [MockStatement(50), MockStatement(101)]
        container = MockContainer(items)

        issues = check_id_range(container, "SRTYP", 1, 100)

        assert len(issues) == 1
        assert issues[0].severity == "error"
        assert "must be between 1 and 100" in issues[0].message

    def test_multiple_out_of_range(self):
        """Test with multiple IDs out of range - should return multiple issues."""
        items = [MockStatement(0), MockStatement(50), MockStatement(101)]
        container = MockContainer(items)

        issues = check_id_range(container, "TETYP", 1, 100)

        assert len(issues) == 2

    def test_boundary_values(self):
        """Test boundary values are included in valid range."""
        items = [MockStatement(1), MockStatement(99999999)]
        container = MockContainer(items)

        issues = check_id_range(container, "RETYP", 1, 99999999)

        assert len(issues) == 0


class TestCheckPositiveValues:
    """Tests for check_positive_values function."""

    def test_all_positive(self):
        """Test with all positive values - should return no issues."""
        stmt = MockStatement(1, ar=10.5, nr=8, di=0.025)

        issues = check_positive_values(
            stmt, "RETYP", {"ar": "area", "nr": "number", "di": "diameter"}
        )

        assert len(issues) == 0

    def test_zero_value(self):
        """Test with zero value - should return issue."""
        stmt = MockStatement(1, ar=0, nr=8)

        issues = check_positive_values(stmt, "RETYP", {"ar": "area", "nr": "number"})

        assert len(issues) == 1
        assert issues[0].severity == "error"
        assert "must be positive" in issues[0].message
        assert "AR=0" in issues[0].message

    def test_negative_value(self):
        """Test with negative value - should return issue."""
        stmt = MockStatement(1, ar=-5.5, nr=8)

        issues = check_positive_values(stmt, "SRTYP", {"ar": "area", "nr": "number"})

        assert len(issues) == 1
        assert "must be positive" in issues[0].message

    def test_none_value(self):
        """Test with None value - should be ignored."""
        stmt = MockStatement(1, ar=None, nr=8)

        issues = check_positive_values(stmt, "RETYP", {"ar": "area", "nr": "number"})

        assert len(issues) == 0

    def test_multiple_invalid(self):
        """Test with multiple invalid values - should return multiple issues."""
        stmt = MockStatement(1, ar=0, nr=-5, di=0.025)

        issues = check_positive_values(
            stmt, "TETYP", {"ar": "area", "nr": "number", "di": "diameter"}
        )

        assert len(issues) == 2


class TestCheckNonNegativeValues:
    """Tests for check_non_negative_values function."""

    def test_positive_value(self):
        """Test with positive value - should return no issues."""
        stmt = MockStatement(1, os=10.5)

        issues = check_non_negative_values(stmt, "RETYP", {"os": "offset"})

        assert len(issues) == 0

    def test_zero_value(self):
        """Test with zero value - should return no issues."""
        stmt = MockStatement(1, os=0)

        issues = check_non_negative_values(stmt, "RETYP", {"os": "offset"})

        assert len(issues) == 0

    def test_negative_value(self):
        """Test with negative value - should return issue."""
        stmt = MockStatement(1, os=-5.5)

        issues = check_non_negative_values(stmt, "RETYP", {"os": "offset"})

        assert len(issues) == 1
        assert issues[0].severity == "error"
        assert "cannot be negative" in issues[0].message

    def test_none_value(self):
        """Test with None value - should be ignored."""
        stmt = MockStatement(1, os=None)

        issues = check_non_negative_values(stmt, "RETYP", {"os": "offset"})

        assert len(issues) == 0


class TestCheckLabelLength:
    """Tests for check_label_length function."""

    def test_valid_length(self):
        """Test with label within limit - should return no issues."""
        stmt = MockStatement(1, lb="ValidLabel")

        issues = check_label_length(stmt, "RETYP", max_length=16)

        assert len(issues) == 0

    def test_exact_max_length(self):
        """Test with label exactly at max length - should return no issues."""
        stmt = MockStatement(1, lb="A" * 16)

        issues = check_label_length(stmt, "RETYP", max_length=16)

        assert len(issues) == 0

    def test_exceeds_length(self):
        """Test with label exceeding max length - should return issue."""
        stmt = MockStatement(1, lb="ThisLabelIsTooLong123")

        issues = check_label_length(stmt, "SRTYP", max_length=16)

        assert len(issues) == 1
        assert issues[0].severity == "error"
        assert "exceeds 16 characters" in issues[0].message

    def test_none_label(self):
        """Test with None label - should return no issues."""
        stmt = MockStatement(1, lb=None)

        issues = check_label_length(stmt, "RETYP", max_length=16)

        assert len(issues) == 0

    def test_custom_field_name(self):
        """Test with custom field name."""
        stmt = MockStatement(1, name="TooLongName12345678")

        issues = check_label_length(
            stmt, "TEST", max_length=16, label_field="name"
        )

        assert len(issues) == 1


class TestCheckMaterialReference:
    """Tests for check_material_reference function."""

    def test_valid_reference(self):
        """Test with valid material reference - should return no issues."""
        stmt = MockStatement(1, mp=10)
        material_container = MockContainer([MockStatement(10), MockStatement(20)])
        model = MockModel(rmpec=material_container)

        issues = check_material_reference(stmt, "RETYP", model, "rmpec")

        assert len(issues) == 0

    def test_invalid_reference(self):
        """Test with invalid material reference - should return issue."""
        stmt = MockStatement(1, mp=999)
        material_container = MockContainer([MockStatement(10), MockStatement(20)])
        model = MockModel(rmpec=material_container)

        issues = check_material_reference(stmt, "SRTYP", model, "rmpec")

        assert len(issues) == 1
        assert issues[0].severity == "error"
        assert "not found in RMPEC" in issues[0].message

    def test_missing_container(self):
        """Test with missing material container - should return issue."""
        stmt = MockStatement(1, mp=10)
        model = MockModel()  # No containers

        issues = check_material_reference(stmt, "TETYP", model, "temat")

        assert len(issues) == 1
        assert "container not found" in issues[0].message

    def test_none_material(self):
        """Test with None material reference - should return no issues."""
        stmt = MockStatement(1, mp=None)
        model = MockModel()

        issues = check_material_reference(stmt, "RETYP", model, "rmpec")

        assert len(issues) == 0


class TestCheckUnusedDefinition:
    """Tests for check_unused_definition function."""

    def test_used_definition(self):
        """Test with definition that is referenced - should return no issues."""
        stmt = MockStatement(1)
        referencing_items = [MockStatement(100, rt=1), MockStatement(101, rt=2)]
        ref_container = MockContainer(referencing_items)
        model = MockModel(reloc=ref_container)

        issues = check_unused_definition(stmt, "RETYP", model, "reloc", "rt")

        assert len(issues) == 0

    def test_unused_definition(self):
        """Test with definition that is not referenced - should return warning."""
        stmt = MockStatement(1)
        referencing_items = [MockStatement(100, rt=2), MockStatement(101, rt=3)]
        ref_container = MockContainer(referencing_items)
        model = MockModel(reloc=ref_container)

        issues = check_unused_definition(stmt, "RETYP", model, "reloc", "rt")

        assert len(issues) == 1
        assert issues[0].severity == "warning"
        assert "not referenced" in issues[0].message

    def test_missing_container(self):
        """Test with missing referencing container - should return no issues."""
        stmt = MockStatement(1)
        model = MockModel()  # No containers

        issues = check_unused_definition(stmt, "TETYP", model, "teloc", "rt")

        assert len(issues) == 0

    def test_empty_container(self):
        """Test with empty referencing container - should return warning."""
        stmt = MockStatement(1)
        ref_container = MockContainer([])
        model = MockModel(srloc=ref_container)

        issues = check_unused_definition(stmt, "SRTYP", model, "srloc", "rt")

        assert len(issues) == 1
        assert issues[0].severity == "warning"


class TestIntegration:
    """Integration tests using utility functions together."""

    def test_multiple_utilities_on_statement(self):
        """Test using multiple utility functions on same statement."""
        # Create statement with multiple issues
        stmt = MockStatement(1, ar=-5, nr=0, lb="ThisLabelIsTooLongForValidation")

        issues = []
        issues.extend(
            check_positive_values(stmt, "RETYP", {"ar": "area", "nr": "number"})
        )
        issues.extend(check_label_length(stmt, "RETYP", max_length=16))

        # Should have 3 issues: 2 for negative/zero values, 1 for label
        assert len(issues) == 3
        assert all(issue.severity == "error" for issue in issues)

    def test_container_with_multiple_checks(self):
        """Test container with duplicate IDs and range checks."""
        items = [MockStatement(0), MockStatement(1), MockStatement(1), MockStatement(101)]
        container = MockContainer(items)

        issues = []
        issues.extend(check_duplicate_ids(container, "RETYP"))
        issues.extend(check_id_range(container, "RETYP", 1, 100))

        # Should have 3 issues: 1 duplicate, 2 out of range
        assert len(issues) == 3
