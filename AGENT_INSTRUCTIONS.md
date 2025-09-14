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