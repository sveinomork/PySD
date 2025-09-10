from typing import Dict, List, Optional, Any
from functools import lru_cache
import threading
from dataclasses import dataclass, field

# 1. Efficient container with O(1) lookups
class OptimizedContainer:
    def __init__(self):
        self._items: Dict[Any, Any] = {}
        self._insertion_order: List[Any] = []
        # Cache for expensive operations
        self._id_cache: Optional[List[Any]] = None
        self._cache_lock = threading.RLock()
    
    def add(self, item: Any) -> None:
        id_val = getattr(item, 'identifier', getattr(item, 'id', None))
        if id_val in self._items:
            raise ValueError(f"Duplicate ID: {id_val}")
        
        self._items[id_val] = item
        self._insertion_order.append(id_val)
        # Invalidate cache
        self._id_cache = None
    
    def get_by_id(self, id_val: Any) -> Optional[Any]:
        """O(1) lookup instead of O(n)"""
        return self._items.get(id_val)
    
    def get_all_ids(self) -> List[Any]:
        """Cached ID list generation"""
        if self._id_cache is None:
            with self._cache_lock:
                if self._id_cache is None:
                    self._id_cache = self._insertion_order.copy()
        return self._id_cache

# 2. Efficient string building for BASCO
@dataclass
class OptimizedBASCO:
    id: int
    load_cases: List[Any]
    typ: Optional[str] = None
    ldf: Optional[int] = None
    txt: Optional[str] = None
    _input_cache: str = field(default="", init=False)
    _cache_valid: bool = field(default=False, init=False)
    
    @property
    def input(self) -> str:
        """Cached input string generation"""
        if not self._cache_valid:
            self._input_cache = self._build_input_optimized()
            self._cache_valid = True
        return self._input_cache
    
    def _build_input_optimized(self) -> str:
        """Optimized string building using list joining"""
        parts = [f"BASCO ID={self.id}"]
        
        if self.ldf is not None:
            parts.append(f"LDF={self.ldf}")
        if self.typ:
            parts.append(f"TYP={self.typ}")
        
        # Build load case parts efficiently
        case_parts = []
        for lc in self.load_cases:
            case_parts.append(f"LF={lc.lc_fact} {lc.lc_type}={lc.lc_numb}")
        
        # Smart line breaking
        base_line = " ".join(parts)
        result_lines = [base_line]
        
        current_line_parts = [base_line]
        current_length = len(base_line)
        
        for case_part in case_parts:
            test_length = current_length + len(case_part) + 1
            if test_length > 100 and len(current_line_parts) > 1:
                # Start new line
                result_lines.append(" ".join(current_line_parts))
                current_line_parts = [base_line, case_part]
                current_length = len(base_line) + len(case_part) + 1
            else:
                current_line_parts.append(case_part)
                current_length = test_length
        
        # Add final line
        if len(current_line_parts) > 1:
            final_line = " ".join(current_line_parts)
            if self.txt:
                txt_part = f"TXT={self.txt}"
                if len(final_line) + len(txt_part) + 1 <= 100:
                    final_line += f" {txt_part}"
                else:
                    result_lines.append(final_line)
                    final_line = f"{base_line} {txt_part}"
            result_lines.append(final_line)
        
        return "\n".join(result_lines)
    
    def invalidate_cache(self):
        """Call when object is modified"""
        self._cache_valid = False

# 3. Validation caching
class ValidationCache:
    def __init__(self, max_size: int = 1000):
        self._cache: Dict[str, List[Any]] = {}
        self._max_size = max_size
        self._lock = threading.RLock()
    
    def get_validation_key(self, obj: Any, context_hash: int) -> str:
        """Generate cache key for validation results"""
        obj_hash = hash((type(obj), getattr(obj, 'id', id(obj))))
        return f"{obj_hash}_{context_hash}"
    
    @lru_cache(maxsize=1000)
    def get_cached_validation(self, obj_key: str) -> Optional[List[Any]]:
        """Get cached validation results"""
        return self._cache.get(obj_key)
    
    def cache_validation(self, obj_key: str, results: List[Any]) -> None:
        """Cache validation results"""
        with self._lock:
            if len(self._cache) >= self._max_size:
                # Simple LRU: remove oldest entries
                oldest_keys = list(self._cache.keys())[:self._max_size // 10]
                for key in oldest_keys:
                    del self._cache[key]
            
            self._cache[obj_key] = results

# 4. Batch validation
class BatchValidator:
    def __init__(self, cache: ValidationCache):
        self._cache = cache
    
    def validate_batch(self, items: List[Any], context: Any) -> Dict[Any, List[Any]]:
        """Validate multiple items efficiently"""
        results = {}
        context_hash = hash(str(context))
        
        # Group by type for batch processing
        by_type: Dict[type, List[Any]] = {}
        for item in items:
            item_type = type(item)
            if item_type not in by_type:
                by_type[item_type] = []
            by_type[item_type].append(item)
        
        # Process each type as a batch
        for item_type, type_items in by_type.items():
            type_results = self._validate_type_batch(type_items, context, context_hash)
            results.update(type_results)
        
        return results
    
    def _validate_type_batch(self, items: List[Any], context: Any, context_hash: int) -> Dict[Any, List[Any]]:
        """Validate items of the same type together"""
        results = {}
        
        for item in items:
            cache_key = self._cache.get_validation_key(item, context_hash)
            cached_result = self._cache.get_cached_validation(cache_key)
            
            if cached_result is not None:
                results[item] = cached_result
            else:
                # Perform actual validation
                validation_result = self._perform_validation(item, context)
                results[item] = validation_result
                self._cache.cache_validation(cache_key, validation_result)
        
        return results
    
    def _perform_validation(self, item: Any, context: Any) -> List[Any]:
        """Placeholder for actual validation logic"""
        # Implementation depends on your validation system
        return []

# Example usage
validation_cache = ValidationCache(max_size=2000)
batch_validator = BatchValidator(validation_cache)

# Use optimized containers
container = OptimizedContainer()
basco = OptimizedBASCO(id=101, load_cases=[])
container.add(basco)

# Efficient lookups
found_item = container.get_by_id(101)  # O(1) instead of O(n)
