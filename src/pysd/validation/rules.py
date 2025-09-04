# validation/rules.py
from .registry import register_rule
from .context import ValidationContext, ValidationIssue

@register_rule
def reloc_must_reference_existing_retyp(ctx: ValidationContext):
    issues: list[ValidationIssue] = []
    retyp_by_id = ctx.model.retyp.by_id()
    for reloc in ctx.model.reloc.items:
        # reloc.rt can be int or (int,int); validate both ends exist
        if isinstance(reloc.rt, tuple):
            rt_ids = (reloc.rt[0], reloc.rt[1])
        else:
            rt_ids = (reloc.rt, )

        for rid in rt_ids:
            if rid not in retyp_by_id:
                issues.append(ctx.error(
                    loc=f"RELOC[id='{reloc.id}']",
                    message=f"References RETYP id={rid} that does not exist",
                    rule_id="RELOC-RETYP-001"
                ))
    return issues

def ensure_id_within_8_digits(id_val: int, loc: str, ctx: ValidationContext, rule_id="ID-RANGE-001"):
    if id_val <= 0 or id_val >= 10**8:
        return [ctx.error(loc=loc, message="ID must be 1..99999999", rule_id=rule_id)]
    return []