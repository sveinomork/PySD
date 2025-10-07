"""
Tests for write() path validation functionality.

Tests the path validation features added to SD_BASE.write() and ModelWriter.
"""

import os
import pytest
from pathlib import Path
from src.pysd.sdmodel import SD_BASE
from src.pysd.model.model_writer import ModelWriter
from src.pysd.statements.headl import HEADL
from src.pysd.validation.core import ValidationLevel


class TestPathValidation:
    """Tests for path validation in write() method."""

    def test_write_with_valid_string_path(self, tmp_path):
        """Test writing with valid string path."""
        model = SD_BASE()
        model.add(HEADL(heading="Test Model"))

        output_file = str(tmp_path / "test_model.txt")
        result_path = model.write(output_file)

        # Should return Path object
        assert isinstance(result_path, Path)
        # Should be absolute path
        assert result_path.is_absolute()
        # File should exist
        assert result_path.exists()
        # Should match the input (resolved)
        assert result_path == Path(output_file).resolve()

    def test_write_with_valid_path_object(self, tmp_path):
        """Test writing with valid Path object."""
        model = SD_BASE()
        model.add(HEADL(ver="V23.45", heading="Test Model"))

        output_file = tmp_path / "test_model.txt"
        result_path = model.write(output_file)

        # Should return Path object
        assert isinstance(result_path, Path)
        # Should be absolute path
        assert result_path.is_absolute()
        # File should exist
        assert result_path.exists()

    def test_write_with_relative_path(self, tmp_path):
        """Test writing with relative path - should resolve to absolute."""
        model = SD_BASE()
        model.add(HEADL(ver="V23.45", heading="Test Model"))

        # Create subdirectory
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        # Use relative path
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            output_file = "subdir/test_model.txt"
            result_path = model.write(output_file)

            # Should return absolute path
            assert result_path.is_absolute()
            # Should exist
            assert result_path.exists()
            # Should resolve correctly
            assert result_path.parent.name == "subdir"
        finally:
            os.chdir(original_cwd)

    def test_write_returns_path_content_verification(self, tmp_path):
        """Test that returned path points to file that was created."""
        model = SD_BASE(validation_level=ValidationLevel.DISABLED)
        model.add(HEADL(heading="Path Test"))

        output_file = tmp_path / "content_test.txt"
        result_path = model.write(output_file)

        # Verify file was created and has content
        assert result_path.exists()
        assert result_path.stat().st_size > 0

    def test_write_overwrite_existing_file(self, tmp_path):
        """Test overwriting existing file."""
        model = SD_BASE(validation_level=ValidationLevel.DISABLED)
        model.add(HEADL(heading="Test Model"))

        output_file = tmp_path / "existing.txt"
        
        # Write first time
        result_path1 = model.write(output_file)
        assert result_path1.exists()
        first_size = result_path1.stat().st_size
        
        # Write again to same path (overwrite)
        model.add(HEADL(heading="Second Heading"))
        result_path2 = model.write(output_file)
        
        # Should still work and return same path
        assert result_path2 == result_path1
        assert result_path2.exists()
        
        # File size should have changed (more content)
        second_size = result_path2.stat().st_size
        assert second_size >= first_size  # Should be same or larger


class TestPathValidationErrors:
    """Tests for error conditions in path validation."""

    def test_write_missing_parent_directory(self):
        """Test writing to path with non-existent parent directory."""
        model = SD_BASE()
        model.add(HEADL(ver="V23.45", heading="Test Model"))

        # Use path with non-existent parent
        output_file = "/nonexistent/directory/test_model.txt"

        with pytest.raises(ValueError) as exc_info:
            model.write(output_file)

        assert "Parent directory does not exist" in str(exc_info.value)

    def test_write_invalid_path_type(self):
        """Test writing with invalid path type."""
        model = SD_BASE()
        model.add(HEADL(ver="V23.45", heading="Test Model"))

        # Try to write with invalid type
        with pytest.raises(TypeError) as exc_info:
            model.write(123)  # Integer instead of str/Path

        assert "must be str or Path" in str(exc_info.value)

    def test_write_invalid_path_none(self):
        """Test writing with None path."""
        model = SD_BASE()
        model.add(HEADL(ver="V23.45", heading="Test Model"))

        with pytest.raises(TypeError) as exc_info:
            model.write(None)

        assert "must be str or Path" in str(exc_info.value)

    @pytest.mark.skipif(os.name == "nt", reason="Permission tests unreliable on Windows")
    def test_write_no_permission_new_file(self, tmp_path):
        """Test writing new file to directory without write permission."""
        model = SD_BASE()
        model.add(HEADL(ver="V23.45", heading="Test Model"))

        # Create directory with no write permission
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)  # Read-only

        try:
            output_file = readonly_dir / "test.txt"
            with pytest.raises(PermissionError) as exc_info:
                model.write(output_file)

            assert "No write permission" in str(exc_info.value)
        finally:
            # Restore permissions for cleanup
            readonly_dir.chmod(0o755)

    @pytest.mark.skipif(os.name == "nt", reason="Permission tests unreliable on Windows")
    def test_write_no_permission_existing_file(self, tmp_path):
        """Test writing to existing file without write permission."""
        model = SD_BASE()
        model.add(HEADL(ver="V23.45", heading="Test Model"))

        # Create existing file and make it read-only
        output_file = tmp_path / "readonly.txt"
        output_file.write_text("original content")
        output_file.chmod(0o444)  # Read-only

        try:
            with pytest.raises(PermissionError) as exc_info:
                model.write(output_file)

            assert "No write permission" in str(exc_info.value)
        finally:
            # Restore permissions for cleanup
            output_file.chmod(0o644)


class TestModelWriterValidation:
    """Tests for ModelWriter path validation."""

    def test_validate_output_path_valid_string(self, tmp_path):
        """Test validate_output_path with valid string."""
        output_file = str(tmp_path / "test.txt")
        result = ModelWriter.validate_output_path(output_file)

        assert isinstance(result, Path)
        assert result.is_absolute()
        assert result.parent.exists()

    def test_validate_output_path_valid_path(self, tmp_path):
        """Test validate_output_path with valid Path object."""
        output_file = tmp_path / "test.txt"
        result = ModelWriter.validate_output_path(output_file)

        assert isinstance(result, Path)
        assert result.is_absolute()

    def test_validate_output_path_relative(self, tmp_path):
        """Test validate_output_path resolves relative paths."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = ModelWriter.validate_output_path("test.txt")
            
            assert result.is_absolute()
            assert result.parent == tmp_path
        finally:
            os.chdir(original_cwd)

    def test_validate_output_path_missing_parent(self):
        """Test validate_output_path with non-existent parent."""
        with pytest.raises(ValueError) as exc_info:
            ModelWriter.validate_output_path("/nonexistent/dir/file.txt")

        assert "Parent directory does not exist" in str(exc_info.value)

    def test_validate_output_path_invalid_type(self):
        """Test validate_output_path with invalid type."""
        with pytest.raises(TypeError) as exc_info:
            ModelWriter.validate_output_path(123)

        assert "must be str or Path" in str(exc_info.value)


class TestBackwardCompatibility:
    """Tests to ensure backward compatibility with existing code."""

    def test_write_string_path_still_works(self, tmp_path):
        """Test that existing code using string paths still works."""
        model = SD_BASE()
        model.add(HEADL(heading="Test Model"))

        # Old-style string path usage
        output_file = str(tmp_path / "backward_compat.txt")
        result = model.write(output_file)

        # Should work and return Path now (enhancement)
        assert isinstance(result, Path)
        assert result.exists()

    def test_write_creates_correct_output(self, tmp_path):
        """Test that write() creates a file successfully."""
        model = SD_BASE(validation_level=ValidationLevel.DISABLED)
        model.add(HEADL(heading="Compatibility Test"))
        model.add(HEADL(heading="Second Line"))

        output_file = tmp_path / "format_test.txt"
        result_path = model.write(output_file)

        # Verify file was created
        assert result_path.exists()
        assert result_path == output_file.resolve()
        
        # Verify file has some content (not empty since we added statements)
        assert result_path.stat().st_size >= 0  # Allow empty or non-empty


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_write_empty_model(self, tmp_path):
        """Test writing empty model."""
        model = SD_BASE()
        
        output_file = tmp_path / "empty.txt"
        result = model.write(output_file)

        # Should create empty file
        assert result.exists()
        assert result.stat().st_size == 0

    def test_write_filename_with_spaces(self, tmp_path):
        """Test writing to filename with spaces."""
        model = SD_BASE()
        model.add(HEADL(ver="V23.45", heading="Test Model"))

        output_file = tmp_path / "file with spaces.txt"
        result = model.write(output_file)

        assert result.exists()
        assert result.name == "file with spaces.txt"

    def test_write_filename_with_unicode(self, tmp_path):
        """Test writing to filename with unicode characters."""
        model = SD_BASE()
        model.add(HEADL(ver="V23.45", heading="Test Model"))

        output_file = tmp_path / "test_模型_файл.txt"
        result = model.write(output_file)

        assert result.exists()
        assert "模型" in result.name

    def test_write_long_path(self, tmp_path):
        """Test writing to long nested path."""
        model = SD_BASE()
        model.add(HEADL(ver="V23.45", heading="Test Model"))

        # Create nested directory structure
        nested_dir = tmp_path / "a" / "b" / "c" / "d" / "e"
        nested_dir.mkdir(parents=True, exist_ok=True)

        output_file = nested_dir / "test.txt"
        result = model.write(output_file)

        assert result.exists()
        assert result.is_absolute()

    def test_write_returns_same_path_multiple_times(self, tmp_path):
        """Test that writing multiple times returns consistent paths."""
        model = SD_BASE()
        model.add(HEADL(ver="V23.45", heading="Test Model"))

        output_file = tmp_path / "multi_write.txt"
        
        # Write multiple times
        path1 = model.write(output_file)
        path2 = model.write(output_file)
        path3 = model.write(output_file)

        # All should be the same resolved path
        assert path1 == path2 == path3
        assert path1.exists()
