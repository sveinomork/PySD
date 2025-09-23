# PySD Refactoring Plan: Simplifying sdmodel.py

## 🎯 **Primary Goal**
Make `src/pysd/sdmodel.py` **shorter and simpler** to enable easy implementation of new statements, rather than modifying `main.py` functionality.

## 📊 **Current Status**
- **Current**: `sdmodel.py` now **325 lines** (reduced from 600+ originally)
- **Extracted**: **481 lines** across 3 focused modules  
- **Phases Completed**: **3 of 4** (Validation, Routing, Container Factory)
- **Goal Achieved**: ✅ sdmodel.py is much shorter and simpler

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

### **Phase 3: Container Factory** ✅ **COMPLETED**
**Priority**: ✅ **DONE** (Organization & Registry)
**Lines Added**: +50 lines (src/pysd/model/container_factory.py)
**New File**: ✅ `src/pysd/model/container_factory.py`

#### **Problem Solved:**
- 20+ container types needed centralized management
- No registry of available container types
- Adding new statement types required scattered changes

#### **Solution Implemented:**
```python
class ContainerFactory:
    """Centralized container management and registry."""
    
    # Registry of all 20 container types
    CONTAINER_TYPES = {
        'greco': GRECO,
        'basco': BASCO, 
        'loadc': LOADC,
        # ... all 20 containers
    }
    
    @classmethod
    def get_container_names(cls) -> List[str]:
        """Get all registered container names."""
        return list(cls.CONTAINER_TYPES.keys())
    
    @classmethod
    def is_valid_container(cls, name: str) -> bool:
        """Check if container type is registered."""
        return name in cls.CONTAINER_TYPES
```

#### **Benefits Achieved:**
- ✅ **Centralized registry**: 20 container types managed in one place
- ✅ **Utility methods**: Validation and lookup functions  
- ✅ **Better organization**: Container management patterns centralized
- ✅ **Extensibility foundation**: Easy to add new statement types
- ✅ **All functionality preserved**: No breaking changes

#### **Key Insight:**
Dynamic field generation not feasible with Pydantic due to timing issues. Static field definitions with centralized registry provides good organization and extensibility benefits.

---

### **Phase 4: Model Writer Extraction** ✅ **COMPLETED**
**Priority**: ✅ **DONE** (Simple I/O extraction)
**Lines Extracted**: 42 lines (only I/O logic)
**New File**: ✅ `src/pysd/model/model_writer.py`

#### **Problem Solved:**
- File I/O logic mixed with model structure in SD_BASE
- `create_writer()` method contained file writing code

#### **Simple Solution:**
```python
class ModelWriter:
    """Simple writer - extracts ONLY file I/O from SD_BASE."""
    
    def write_to_file(self, output_file: str) -> None:
        """Same file writing logic as before."""
        with open(output_file, "w", encoding="utf-8") as f:
            for item in self.model.all_items:
                f.write(str(item) + "\n")
```

#### **Benefits Achieved:**
- ✅ **I/O logic extracted**: File writing moved out of SD_BASE
- ✅ **No new features**: Only original functionality moved
- ✅ **Backward compatible**: main.py works unchanged
- ✅ **Simple and focused**: No over-engineering

#### **Key Principle:**
**Only extracted existing functionality - no new features added.**

---
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