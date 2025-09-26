from typing import Optional
from ..statements.greco import GRECO
from ..statements.loadc import LoadcList
from ..statements.basco import BASCO, LoadCase


def convert_to_only_olcs(
    basco_input: list[BASCO],
    target_id: int,
    alc_olc_mapping: Optional["LoadcList"] = None,
    grecos: Optional[list["GRECO"]] = None,
    load_resultant_str: Optional[str] = None,
) -> BASCO:
    """
    Convert a BASCO that contains BAS and ELC references to one that only contains OLCs.

    Args:
        basco_input: List of all BASCO statements to search through
        target_id: ID of the BASCO to convert
        alc_olc_mapping: LoadcList for ELC to OLC mapping (required for ELC conversion)
        grecos: List of GRECO statements (required for ELC conversion)
        load_resultant_str: Load resultant data string (required for ELC conversion)

    Returns:
        New BASCO with only OLC load cases, with factors calculated by:
        - Direct OLC cases: keep as-is
        - BAS references: expand and multiply factors
        - ELC references: calculate equilibrium factors and expand to OLCs

    Logic:
        For each BAS reference with factor F:
        1. Find the referenced BASCO by ID
        2. For each OLC in that BASCO with factor G:
           - Add/combine to result with factor F * G

        For each ELC reference with factor F:
        1. Calculate equilibrium factors for balancing OLCs
        2. Add OLC cases with factors = F * equilibrium_factor

    Example:
        BASCO 201: ELC=201 LF=10, ELC=202 LF=10
        Result: OLC cases with calculated equilibrium factors
    """
    # Create lookup dictionary for quick BASCO access
    basco_lookup = {basco.id: basco for basco in basco_input}

    # Find the target BASCO
    if target_id not in basco_lookup:
        raise ValueError(f"BASCO with ID {target_id} not found")

    target_basco = basco_lookup[target_id]

    # Dictionary to accumulate OLC factors {olc_number: total_factor}
    olc_factors: dict[int, float] = {}

    # Process each load case in the target BASCO
    for load_case in target_basco.load_cases:
        if load_case.lc_type == "OLC":
            # Direct OLC case - add to result
            olc_num = load_case.lc_numb
            olc_factors[olc_num] = olc_factors.get(olc_num, 0) + load_case.lc_fact

        elif load_case.lc_type == "BAS":
            # BAS reference - expand to OLCs
            bas_id = load_case.lc_numb
            bas_factor = load_case.lc_fact

            if bas_id not in basco_lookup:
                raise ValueError(f"Referenced BAS {bas_id} not found")

            # Recursively expand if the referenced BASCO also has BAS references
            expanded_basco = convert_to_only_olcs(
                basco_input, bas_id, alc_olc_mapping, grecos, load_resultant_str
            )

            # Add each OLC from the expanded BASCO with multiplied factor
            for olc_case in expanded_basco.load_cases:
                if olc_case.lc_type == "OLC":
                    olc_num = olc_case.lc_numb
                    combined_factor = bas_factor * olc_case.lc_fact
                    olc_factors[olc_num] = olc_factors.get(olc_num, 0) + combined_factor

        elif load_case.lc_type == "ELC":
            # ELC reference - calculate equilibrium factors and expand to OLCs
            elc_id = load_case.lc_numb
            elc_factor = load_case.lc_fact

            # Check if required parameters are provided for ELC conversion
            if not all([alc_olc_mapping, grecos, load_resultant_str]):
                raise ValueError(
                    "ELC conversion requires alc_olc_mapping, grecos, and load_resultant_str parameters"
                )

            # Import here to avoid circular imports
            from equlibrium.load_factor_calculator import get_elc_factors

            # Get balancing OLCs from GRECO statements (assuming first GRECO contains the balancing OLCs)
            if not grecos:
                raise ValueError("No GRECO statements provided for ELC conversion")

            # Get the balancing OLC numbers from the first GRECO statement
            balancing_olcs = list(grecos[0].bas) if grecos[0].bas else []

            if not balancing_olcs:
                raise ValueError("No balancing OLCs found in GRECO statements")

            # Calculate equilibrium factors for this ELC
            # Type guard to ensure non-None values
            assert load_resultant_str is not None, (
                "load_resultant_str cannot be None for ELC conversion"
            )
            assert alc_olc_mapping is not None, (
                "alc_olc_mapping cannot be None for ELC conversion"
            )
            elc_factors = get_elc_factors(
                load_resultant_str, balancing_olcs, elc_id, alc_olc_mapping
            )

            # Add OLC cases with calculated factors (negative for equilibrium)
            for i, balancing_olc in enumerate(balancing_olcs):
                if i < len(elc_factors):  # Safety check
                    combined_factor = elc_factor * (
                        -elc_factors[i]
                    )  # Negative for equilibrium
                    olc_factors[balancing_olc] = (
                        olc_factors.get(balancing_olc, 0) + combined_factor
                    )

            # Also add the original ELC as OLC (direct mapping)
            olc_factors[elc_id] = olc_factors.get(elc_id, 0) + elc_factor

    # Create new load cases from accumulated factors
    new_load_cases = [
        LoadCase(lc_type="OLC", lc_numb=olc_num, lc_fact=factor)
        for olc_num, factor in sorted(olc_factors.items())
    ]

    # Create new BASCO with only OLC cases
    return BASCO(
        id=target_id,
        load_cases=new_load_cases,
        typ=target_basco.typ,
        ldf=target_basco.ldf,
        txt=target_basco.txt,
    )
