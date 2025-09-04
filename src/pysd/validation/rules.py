# validation/rules.py
from .registry import register_rule
from .context import ValidationContext, ValidationIssue

@register_rule
def greco_must_contain_bas_id(ctx: ValidationContext):
    pass
   
