# PySD Refactoring Plan: Simplifying sdmodel.py

## 🎯 **Primary Goal**
Make `src/pysd/sdmodel.py` **shorter and simpler** to enable easy implementation of new statements, rather than modifying `main.py` functionality.

## 📊 **Current Status**
- **Current**: `sdmodel.py` ~430 lines
- **Target**: `sdmodel.py` ~150 lines (**65% reduction**)
- **Phase 1**: ✅ **COMPLETED** - ValidationManager extraction (~110 lines moved)

---

## **Problem Analysis**

The main complexity in `sdmodel.py` comes from:

1. **Massive `_route_item()` method** (50+ lines of if/elif statements)
2. **Duplicate `_add_batch()` logic** (40+ lines of similar if/elif)
3. **Complex validation logic mixed with routing** (moved to ValidationManager ✅)
4. **Hard to add new statements** - requires changes in multiple places

---

## **Refactoring Phases**

### **Phase 1: ✅ ValidationManager Extraction (COMPLETED)**
**Status**: ✅ Done
**Lines Reduced**: ~110 lines
**New File**: `src/pysd/model/validation_manager.py` (143 lines)

**What was extracted:**
- `_validate_cross_references()`
- `_collect_validation_issues()`
- `validate_integrity()` logic
- Cross-validation decision logic
- Model finalization validation

**Benefits Achieved:**
- ✅ ValidationManager handles all validation complexity
- ✅ 20% size reduction in `sdmodel.py`
- ✅ Backward compatibility maintained
- ✅ All existing functionality preserved

---

### **Phase 2: Statement Router Extraction** ✅ **COMPLETED**
**Priority**: 🔥 **HIGH** (Biggest impact for statement implementation)
**Status**: ✅ **DONE** - Successfully implemented and tested
**Lines Reduced**: 118 lines from sdmodel.py (445 → 327)
**New File**: `src/pysd/model/statement_router.py` (177 lines)

#### **Current Problem:**
```python
# Adding a new statement requires editing multiple methods
def _route_item(self, item: StatementType) -> None:
    # 50+ lines of if/elif...
    elif isinstance(item, GRECO):
        self.greco.add(item)
    elif isinstance(item, BASCO):
        self.basco.add(item)
    # ... 20+ more statements
    elif isinstance(item, NEW_STATEMENT):  # ← Must add here
        self.new_statement.add(item)
        
def _add_batch(self, items: List[StatementType]) -> None:
    # 40+ lines of similar if/elif...
    elif item_type == GRECO:
        self.greco.add_batch(type_items)
    # ... 20+ more statements  
    elif item_type == NEW_STATEMENT:  # ← And here
        self.new_statement.add_batch(type_items)
```

#### **Solution: Registry Pattern**
```python
class StatementRouter:
    """Handles all statement routing with a simple registry."""
    
    # Single source of truth for routing
    _routing_registry = {
        GRECO: 'greco',
        BASCO: 'basco',
        LOADC: 'loadc',
        # ... all statements in one place
    }
    
    def route_item(self, item: StatementType, model: SD_BASE) -> None:
        """Single line routing using registry."""
        container_name = self._routing_registry.get(type(item))
        if container_name:
            getattr(model, container_name).add(item)
        else:
            raise TypeError(f"Unsupported type: {type(item).__name__}")
    
    def route_batch(self, items: List[StatementType], model: SD_BASE) -> None:
        """Batch routing with automatic grouping."""
        # Group by type and batch process
        pass
```

#### **Benefits:**
- ✅ **Adding new statements**: Change 1 line instead of editing 2 methods
- ✅ **Eliminates duplication**: Single routing logic
- ✅ **Easier maintenance**: All routing in one place
- ✅ **Type safety**: Registry validates supported types

---

### **Phase 3: Container Factory**
**Priority**: 🔄 **MEDIUM** (Reduces boilerplate)
**Target Lines Reduced**: ~30 lines
**New File**: `src/pysd/model/container_factory.py`

#### **Current Problem:**
```python
# 20+ repetitive container field definitions
greco: BaseContainer[GRECO] = Field(default_factory=lambda: BaseContainer[GRECO]())
basco: BaseContainer[BASCO] = Field(default_factory=lambda: BaseContainer[BASCO]())
loadc: BaseContainer[LOADC] = Field(default_factory=lambda: BaseContainer[LOADC]())
# ... 20 more similar lines
```

#### **Solution: Dynamic Container Creation**
```python
class ContainerFactory:
    """Creates and manages all model containers."""
    
    @staticmethod
    def create_containers() -> Dict[str, BaseContainer]:
        """Create all containers with proper typing."""
        return {
            'greco': BaseContainer[GRECO](),
            'basco': BaseContainer[BASCO](),
            'loadc': BaseContainer[LOADC](),
            # ... all containers
        }
    
    @staticmethod  
    def generate_container_fields() -> Dict[str, Any]:
        """Generate Pydantic field declarations."""
        # Programmatically create Field definitions
        pass
```

#### **Benefits:**
- ✅ **Eliminates boilerplate**: No repetitive field definitions
- ✅ **Easier maintenance**: Add container in one place
- ✅ **Type consistency**: Centralized container creation logic

---

### **Phase 4: Model Writer Extraction**
**Priority**: 🔄 **MEDIUM** (Cleaner separation)
**Target Lines Reduced**: ~20 lines
**New File**: `src/pysd/model/model_writer.py`

#### **Current Problem:**
```python
# I/O logic mixed with model logic
@classmethod
@contextmanager
def create_writer(cls, output_file: str):
    # Model creation AND file writing in same place
    sd_model = cls()
    try:
        yield sd_model
    finally:
        # File writing logic here
        with open(output_file, "w") as f:
            for item in sd_model.all_items:
                f.write(str(item) + "\n")
```

#### **Solution: Separate I/O Responsibility**
```python
class ModelWriter:
    """Handles all model I/O operations."""
    
    @classmethod
    @contextmanager
    def create_writer(cls, model_class, output_file: str):
        """Clean separation of model creation and file writing."""
        pass
```

#### **Benefits:**
- ✅ **Single Responsibility**: Model class focuses on data, Writer handles I/O
- ✅ **Easier testing**: Test model logic separately from file operations
- ✅ **Flexibility**: Different output formats without changing model

---

## **Impact on Adding New Statements**

### **Current Process (Complex):**
```python
# Step 1: Add import (1 line)
from src.pysd.statements.new_statement import NEW_STATEMENT

# Step 2: Add to type union (1 line)
StatementType = Union[..., NEW_STATEMENT]

# Step 3: Add container field (3 lines)
new_statement: BaseContainer[NEW_STATEMENT] = Field(
    default_factory=lambda: BaseContainer[NEW_STATEMENT](),
    description="NEW_STATEMENT container"
)

# Step 4: Add to _route_item method (2 lines)
elif isinstance(item, NEW_STATEMENT):
    self.new_statement.add(item)

# Step 5: Add to _add_batch method (2 lines)
elif item_type == NEW_STATEMENT:
    self.new_statement.add_batch(type_items)

# Step 6: Add to setup_container_parent_references (1 line)
# Step 7: Add to validation collection (1 line)

# Total: ~11 lines across 7 different locations
```

### **After Refactoring (Simple):**
```python
# Step 1: Add import (1 line)  
from src.pysd.statements.new_statement import NEW_STATEMENT

# Step 2: Add to type union (1 line)
StatementType = Union[..., NEW_STATEMENT]

# Step 3: Add to routing registry (1 line)
StatementRouter._routing_registry[NEW_STATEMENT] = 'new_statement'

# Step 4: Add to container factory (1 line)
ContainerFactory._containers['new_statement'] = BaseContainer[NEW_STATEMENT]

# Total: 4 lines in 4 locations, everything else automatic!
```

---

## **Expected File Structure After All Phases**

```
src/pysd/
├── sdmodel.py (~150 lines) ⭐ Main target
├── model/
│   ├── __init__.py
│   ├── validation_manager.py (143 lines) ✅ Done
│   ├── statement_router.py (~80 lines) 
│   ├── container_factory.py (~50 lines)
│   └── model_writer.py (~30 lines)
```

**Total Lines**: ~453 lines (same functionality, much better organized)
**sdmodel.py Reduction**: 430 → 150 lines (**65% smaller**)

---

## **Implementation Priority**

### **Immediate (High Impact)**
1. ✅ **Phase 1**: ValidationManager (COMPLETED)
2. 🔥 **Phase 2**: StatementRouter (biggest complexity reduction)
3. 🔄 **Phase 3**: ContainerFactory (eliminates boilerplate)

### **Future (Lower Priority)**  
4. **Phase 4**: ModelWriter (cleaner separation)

### **Not Needed (Per User Request)**
- Feature builders for `main.py` (main.py changes not desired)
- Model factories (current approach works fine)

---

## **Success Criteria**

✅ **Phase 1 Success Metrics (Achieved):**
- ValidationManager extracted: ✅
- Backward compatibility maintained: ✅
- All tests still pass: ✅
- File size reduced by ~20%: ✅

🎯 **Overall Success Metrics:**
- [ ] `sdmodel.py` reduced to ~150 lines (65% reduction)
- [ ] Adding new statements requires ≤4 line changes
- [ ] All existing functionality preserved
- [ ] No changes required to `main.py`
- [ ] Improved maintainability and readability

---

## **Next Steps**

1. **Implement Phase 2**: StatementRouter extraction
2. **Test compatibility**: Ensure all existing code works
3. **Validate new statement process**: Test adding a new statement type
4. **Continue to Phase 3** if Phase 2 successful

---

*Last Updated: September 12, 2025*
*Status: Phases 1-2 Complete, Phase 3 Ready for Implementation*