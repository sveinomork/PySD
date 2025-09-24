# PySD Project Instructions for AI Agent

## Critical Rules - READ FIRST

### 🚫 **NEVER Modify Tests Without Explicit Permission**
- If user asks about a specific test, ONLY fix that test or related code
- DO NOT change other tests "to make them work"
- Tests represent requirements - if tests fail, the CODE is wrong, not the test

### 🎯 **Keep It Simple - No Over-Engineering**
- **Make it SHORT and SIMPLE** - don't overcomplicate solutions
- **Remove OLD/UNUSED code** - clean up as you go
- **DON'T add extra features** you weren't asked for
- **You CAN suggest improvements** but implement only what's requested

### ⚠️ **Test Failure Investigation Process**
1. **Understand what the test expects** (read test carefully)
2. **Check if the expectation is correct** (ask user if unclear)
3. **Fix the implementation code** to meet test requirements
4. **Only modify the test if explicitly told to do so**

### 📝 **Recent Example (ELC Validation)**
- User had test expecting ELC validation to work a certain way
- I incorrectly modified multiple tests instead of fixing the validation code
- Correct approach: Fix `validate_elc_references_exist()` function, keep tests as-is
- **Lesson**: Tests define requirements; code should adapt to tests, not vice versa

## Domain-Specific Rules

### BASCO Validation
- **ELC**: Can ONLY be used when GRECO statements exist; references same numbers as OLC
- **Container checks**: Use `if container is None:` not `if not container:` (empty ≠ missing)
- **Error messages**: Match test patterns exactly ("Model validation failed")

### ValidationLevel System
- Use `ValidationLevel.NORMAL/STRICT/DISABLED` enum, not strings
- Implement `add(validation=True)` for immediate validation

## When in Doubt
- **ASK** the user for clarification
- **READ** existing code patterns
- **DON'T ASSUME** - especially about test modifications
- **DON'T implement** - backward compatibility if not spesifically asked

## Documentation Standards

### Statement Docstring Template

Use this standardized template for all statement docstrings:

```python
"""
[Brief description of the statement's purpose - 1-2 sentences]

[Optional: More detailed description including technical context and relationships]

### Examples
```python
# [Description of example 1]
STATEMENT_NAME(param1=value1, param2=value2)
# -> "STATEMENT_NAME PARAM1=value1 PARAM2=value2"

# [Description of example 2 - different use case]  
STATEMENT_NAME(param1=value1, optional_param=value3)
# -> "STATEMENT_NAME PARAM1=value1 OPTIONAL_PARAM=value3"

# [Description of example 3 - complex/advanced case]
STATEMENT_NAME(param1=complex_value, param2=advanced_config)
# -> "STATEMENT_NAME PARAM1=complex_value PARAM2=advanced_config"
```

### Parameters
required_param : type
    Description of required parameter, including constraints and format.
    Additional usage notes or examples if helpful.

optional_param : Optional[type], default=None
    Description of optional parameter and when to use it.
    Mention relationships to other parameters.

flag_param : bool, default=False
    Description of boolean flag behavior.
    Explain what True/False values mean in context.

### Notes
- Important behavioral notes
- Performance considerations
- Relationship to other statements or system components
"""
```

**Key Rules:**
- **ALWAYS** include space after `### ` (three hashes + space)
- **THREE sections only**: Examples, Parameters, Notes
- **NO Validation Rules section** - validation is handled separately
- Use realistic examples from structural engineering domain
- Include expected output with `# ->` arrow format
- Document all parameters with type and default value
- Keep Notes section for important usage information only

**Formatting:**
- Brief description at top (1-2 sentences)
- Examples must show actual parameter values and expected output
- Parameters documented as: `param_name : type, default=value`
- Notes as simple bullet points with `-`