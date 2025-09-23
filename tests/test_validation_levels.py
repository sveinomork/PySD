"""
Test validation levels functionality in SD_BASE.

This module tests that the new validation_level constructor parameter
correctly maps to ValidationLevel enum values and controls validation behavior.
"""

import pytest
from pysd.statements import DECAS, BASCO, LoadCase, LOADC
from pysd.sdmodel import SD_BASE
from pysd.validation.core import ValidationLevel, validation_config


class TestValidationLevels:
    """Test all validation levels: disabled, normal, strict"""
    
    def test_disabled_validation_level(self):
        """Test that 'disabled' validation level disables all validation"""
        model = SD_BASE(validation_level=ValidationLevel.DISABLED)
        
        # Check that validation level is set correctly
        assert validation_config.level == ValidationLevel.DISABLED
        
        # Check that validation flags are disabled
        assert not model.validation_enabled
        assert not model.container_validation_enabled
        assert not model.cross_container_validation_enabled
        
        # Should be able to add invalid statements without error
        model.add(LOADC(run_number=1, alc=1, olc=110))
        # No BASCO defined - this should not raise an error with disabled validation
        decas = DECAS(ls='ULS', bas=999)  # 999 does not exist
        model.add(decas, validation=True)  # Even with validation=True, should not fail
        
        assert decas.input == "DECAS LS=ULS BAS=999"
    
    def test_normal_validation_level(self):
        """Test that 'normal' validation level enables normal validation"""
        model = SD_BASE(validation_level=ValidationLevel.NORMAL)
        
        # Check that validation level is set correctly
        assert validation_config.level == ValidationLevel.NORMAL
        
        # Check that validation flags are enabled
        assert model.validation_enabled
        assert model.container_validation_enabled
        assert model.cross_container_validation_enabled
        
        # Should validate correctly with valid statements
        model.add(LOADC(run_number=1, alc=1, olc=110))
        model.add(BASCO(id=101, load_cases=[LoadCase(lc_type='OLC', lc_numb=110)]))
        
        decas = DECAS(ls='ULS', bas=101)
        model.add(decas, validation=True)  # Should pass validation
        
        assert decas.input == "DECAS LS=ULS BAS=101"
    
    def test_strict_validation_level(self):
        """Test that 'strict' validation level enables strict validation"""
        model = SD_BASE(validation_level=ValidationLevel.STRICT)
        
        # Check that validation level is set correctly
        assert validation_config.level == ValidationLevel.STRICT
        
        # Check that validation flags are enabled
        assert model.validation_enabled
        assert model.container_validation_enabled
        assert model.cross_container_validation_enabled
        
        # Should validate strictly
        model.add(LOADC(run_number=1, alc=1, olc=110))
        model.add(BASCO(id=101, load_cases=[LoadCase(lc_type='OLC', lc_numb=110)]))
        
        decas = DECAS(ls='ULS', bas=101)
        model.add(decas, validation=True)  # Should pass validation
        
        assert decas.input == "DECAS LS=ULS BAS=101"
    
    def test_invalid_validation_level(self):
        """Test that invalid validation level raises error"""
        # With enum, Pydantic will raise a ValidationError for invalid values
        from pydantic_core import ValidationError
        with pytest.raises(ValidationError):
            SD_BASE(validation_level='invalid')  # String instead of enum should cause validation error
    
    def test_cross_object_validation_parameter(self):
        """Test that cross_object_validation parameter works correctly"""
        # With cross_object_validation=False, immediate validation should be disabled by default
        model = SD_BASE(validation_level=ValidationLevel.NORMAL, cross_object_validation=False)
        assert not model.cross_object_validation
        
        # With cross_object_validation=True, immediate validation should be enabled by default  
        model = SD_BASE(validation_level=ValidationLevel.NORMAL, cross_object_validation=True)
        assert model.cross_object_validation
    
    def test_validation_parameter_override(self):
        """Test that add() method validation parameter overrides model setting"""
        model = SD_BASE(validation_level=ValidationLevel.NORMAL, cross_object_validation=False)
        
        model.add(LOADC(run_number=1, alc=1, olc=110))
        model.add(BASCO(id=101, load_cases=[LoadCase(lc_type='OLC', lc_numb=110)]))
        
        # Model has cross_object_validation=False, but validation=True should override
        decas = DECAS(ls='ULS', bas=101)
        model.add(decas, validation=True)  # Should validate despite model setting
        
        assert decas.input == "DECAS LS=ULS BAS=101"
    
    def test_normal_validation_with_error(self):
        """Test that normal validation catches errors"""
        model = SD_BASE(validation_level=ValidationLevel.NORMAL, cross_object_validation=True)
        
        model.add(LOADC(run_number=1, alc=1, olc=110))
        model.add(BASCO(id=101, load_cases=[LoadCase(lc_type='OLC', lc_numb=110)]))
        
        decas = DECAS(ls='ULS', bas=999)  # 999 does not exist
        
        with pytest.raises(ValueError, match=r"DECAS_LOAD_CASES_NOT_FOUND.*references undefined load cases: \[999\]"):
            model.add(decas, validation=True)
    
    def test_strict_validation_with_error(self):
        """Test that strict validation catches errors"""
        model = SD_BASE(validation_level=ValidationLevel.STRICT, cross_object_validation=True)
        
        model.add(LOADC(run_number=1, alc=1, olc=110))
        model.add(BASCO(id=101, load_cases=[LoadCase(lc_type='OLC', lc_numb=110)]))
        
        decas = DECAS(ls='ULS', bas=999)  # 999 does not exist
        
        with pytest.raises(ValueError, match=r"DECAS_LOAD_CASES_NOT_FOUND.*references undefined load cases: \[999\]"):
            model.add(decas, validation=True)
    
    def test_default_parameters(self):
        """Test that default parameters work correctly"""
        # Default should be validation_level=ValidationLevel.NORMAL, cross_object_validation=True
        model = SD_BASE()
        
        assert model.validation_level == ValidationLevel.NORMAL
        assert model.cross_object_validation
        assert validation_config.level == ValidationLevel.NORMAL
    
    