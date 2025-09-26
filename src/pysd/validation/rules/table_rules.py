"""
Validation rules for TABLE statements.
"""

from typing import List, TYPE_CHECKING
from ..rule_system import instance_rule, container_rule, model_rule
from ..core import ValidationIssue, ValidationContext

if TYPE_CHECKING:
    from ...statements.table import TABLE
    from ...model.base_container import BaseContainer


# Instance-level validation rules
@instance_rule("TABLE")
def validate_table_mode(
    table: "TABLE", context: ValidationContext
) -> List[ValidationIssue]:
    """Validate that exactly one of tab or ur is specified."""
    issues = []

    if table.tab is None and table.ur is None:
        issues.append(
            ValidationIssue(
                severity="error",
                code="TABLE_001",
                message="TABLE statement must specify either TAB or UR mode",
                context={"table_id": table.id},
            )
        )
    elif table.tab is not None and table.ur is not None:
        issues.append(
            ValidationIssue(
                severity="error",
                code="TABLE_002",
                message="TABLE statement cannot specify both TAB and UR modes",
                context={"table_id": table.id, "tab": table.tab, "ur": table.ur},
            )
        )

    return issues


@instance_rule("TABLE")
def validate_table_parameters(
    table: "TABLE", context: ValidationContext
) -> List[ValidationIssue]:
    """Validate TABLE parameter consistency."""
    issues = []

    # Validate section ranges
    if table.fs is not None:
        if isinstance(table.fs, tuple) and len(table.fs) != 2:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="TABLE_003",
                    message="FS range must be a tuple of exactly 2 integers",
                    context={"table_id": table.id, "fs": table.fs},
                )
            )
        elif isinstance(table.fs, tuple) and table.fs[0] > table.fs[1]:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="TABLE_004",
                    message="FS range start must be less than or equal to end",
                    context={"table_id": table.id, "fs": table.fs},
                )
            )

    if table.hs is not None:
        if isinstance(table.hs, tuple) and len(table.hs) != 2:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="TABLE_005",
                    message="HS range must be a tuple of exactly 2 integers",
                    context={"table_id": table.id, "hs": table.hs},
                )
            )
        elif isinstance(table.hs, tuple) and table.hs[0] > table.hs[1]:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="TABLE_006",
                    message="HS range start must be less than or equal to end",
                    context={"table_id": table.id, "hs": table.hs},
                )
            )

    # Validate coordinate tuples
    for coord_name, coord_value in [
        ("x1", table.x1),
        ("x2", table.x2),
        ("x3", table.x3),
    ]:
        if coord_value is not None and len(coord_value) != 3:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="TABLE_007",
                    message=f"{coord_name.upper()} coordinate must be a tuple of exactly 3 floats",
                    context={
                        "table_id": table.id,
                        "coordinate": coord_name,
                        "value": coord_value,
                    },
                )
            )

    # Validate element number range
    if table.enr is not None:
        if len(table.enr) != 2:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="TABLE_008",
                    message="ENR (element number range) must be a tuple of exactly 2 integers",
                    context={"table_id": table.id, "enr": table.enr},
                )
            )
        elif table.enr[0] > table.enr[1]:
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="TABLE_009",
                    message="ENR range start must be less than or equal to end",
                    context={"table_id": table.id, "enr": table.enr},
                )
            )

    # Validate coordinate center
    if table.cc is not None and len(table.cc) != 2:
        issues.append(
            ValidationIssue(
                severity="error",
                code="TABLE_010",
                message="CC (coordinate center) must be a tuple of exactly 2 floats",
                context={"table_id": table.id, "cc": table.cc},
            )
        )

    return issues


@instance_rule("TABLE")
def validate_table_mode_specific_parameters(
    table: "TABLE", context: ValidationContext
) -> List[ValidationIssue]:
    """Validate that mode-specific parameters are used correctly."""
    issues = []

    # TAB-specific parameters should only be used with TAB mode
    tab_specific = [
        table.el,
        table.se,
        table.rn,
        table.x1,
        table.x2,
        table.x3,
        table.enr,
        table.cc,
    ]
    if table.tab is None and any(param is not None for param in tab_specific):
        issues.append(
            ValidationIssue(
                severity="warning",
                code="TABLE_011",
                message="TAB-specific parameters used without TAB mode",
                context={"table_id": table.id, "mode": "UR" if table.ur else "None"},
            )
        )

    # UR-specific parameters should only be used with UR mode
    ur_specific = [table.tv, table.sk, table.rl, table.al, table.fa, table.tl]
    ur_specific_bool = [table.fm]
    if table.ur is None and (
        any(param is not None for param in ur_specific) or any(ur_specific_bool)
    ):
        issues.append(
            ValidationIssue(
                severity="warning",
                code="TABLE_012",
                message="UR-specific parameters used without UR mode",
                context={"table_id": table.id, "mode": "TAB" if table.tab else "None"},
            )
        )

    return issues


@instance_rule("TABLE")
def validate_table_file_output(
    table: "TABLE", context: ValidationContext
) -> List[ValidationIssue]:
    """Validate file output parameters."""
    issues = []

    # Cannot use both OF and NF
    if table.of is not None and table.nf is not None:
        issues.append(
            ValidationIssue(
                severity="error",
                code="TABLE_013",
                message="TABLE statement cannot specify both OF (old file) and NF (new file)",
                context={"table_id": table.id, "of": table.of, "nf": table.nf},
            )
        )

    return issues


# Container-level validation rules
@container_rule("TABLE")
def validate_table_uniqueness(
    container: "BaseContainer[TABLE]", context: ValidationContext
) -> List[ValidationIssue]:
    """Validate uniqueness constraints for TABLE statements."""
    issues = []

    # Check for duplicate TABLE configurations
    seen_configs = set()
    for table in container.items:
        # Create a configuration signature
        config = (
            table.tab,
            table.ur,
            table.pa,
            table.fs,
            table.hs,
            table.ls,
            table.ilc,
            table.olc,
            table.elc,
            table.bas,
            table.pha,
        )

        if config in seen_configs:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    code="TABLE_014",
                    message="Duplicate TABLE configuration detected",
                    context={
                        "table_id": table.id,
                        "config": {
                            "tab": table.tab,
                            "ur": table.ur,
                            "pa": table.pa,
                            "fs": table.fs,
                            "hs": table.hs,
                            "ls": table.ls,
                        },
                    },
                )
            )
        else:
            seen_configs.add(config)

    return issues


@container_rule("TABLE")
def validate_table_output_conflicts(
    container: "BaseContainer[TABLE]", context: ValidationContext
) -> List[ValidationIssue]:
    """Validate file output conflicts."""
    issues = []

    # Check for conflicting file outputs
    file_outputs = {}
    for table in container.items:
        output_file = table.of or table.nf
        if output_file:
            if output_file in file_outputs:
                # Check if both are trying to write to same file with different modes
                existing_table = file_outputs[output_file]
                existing_mode = "append" if existing_table.of else "overwrite"
                current_mode = "append" if table.of else "overwrite"

                if existing_mode != current_mode:
                    issues.append(
                        ValidationIssue(
                            severity="warning",
                            code="TABLE_015",
                            message="Conflicting file output modes for same file",
                            context={
                                "file": output_file,
                                "existing_table": existing_table.id,
                                "existing_mode": existing_mode,
                                "current_table": table.id,
                                "current_mode": current_mode,
                            },
                        )
                    )
            else:
                file_outputs[output_file] = table

    return issues


# Model-level validation rules
@model_rule("TABLE")
def validate_table_cross_references(
    statement: "TABLE", context: "ValidationContext"
) -> List[ValidationIssue]:
    """Validate cross-references between TABLE statements and other containers."""
    issues = []

    if context.full_model is None:
        return issues

    model = context.full_model

    # Check if the TABLE statement references a part that exists in DESEC
    if statement.pa:
        # Check against DESEC parts
        if hasattr(model, "desec"):
            desec_parts = set()
            for desec in model.desec.items:
                if hasattr(desec, "pa") and desec.pa:
                    desec_parts.add(desec.pa)

            if statement.pa not in desec_parts:
                available_parts = (
                    ", ".join(sorted(desec_parts)) if desec_parts else "None"
                )
                issues.append(
                    ValidationIssue(
                        severity="error",
                        code="TABLE_PART_NOT_IN_DESEC",
                        message=f'TABLE references structural part "{statement.pa}" not defined in DESEC',
                        location=f"TABLE.{statement.pa}",
                        suggestion=f"Define part in DESEC first or use existing parts: {available_parts}",
                    )
                )
        else:
            # No DESEC container exists at all
            issues.append(
                ValidationIssue(
                    severity="error",
                    code="TABLE_NO_DESEC_CONTAINER",
                    message=f'TABLE part "{statement.pa}" requires DESEC definitions but no DESEC container exists',
                    location=f"TABLE.{statement.pa}",
                    suggestion="Add DESEC statements to define design sections before using TABLE",
                )
            )

    return issues


@model_rule("TABLE")
def validate_table_load_case_references(
    statement: "TABLE", context: "ValidationContext"
) -> List[ValidationIssue]:
    """Validate load case references in TABLE statements."""
    issues = []

    # This is a placeholder for load case validation
    # In a complete implementation, you would check against actual load case containers
    load_cases = [
        statement.ilc,
        statement.olc,
        statement.elc,
        statement.bas,
        statement.pha,
    ]
    load_case_names = ["ILC", "OLC", "ELC", "BAS", "PHA"]

    for lc, name in zip(load_cases, load_case_names):
        if lc is not None:
            # Add validation logic for load case existence
            # This would check against actual load case containers when available
            pass

    return issues
