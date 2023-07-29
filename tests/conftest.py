"""Pytest conftest file."""

from unittest.mock import patch

import pytest


@pytest.fixture(
    autouse=True,
)
def mock_random_array_item():
    """Mock random_array_item to return the species"""
    with patch("myning.utils.utils.get_random_array_item") as mock_species:
        mock_species.return_value = "Alien"

    yield mock_species


@pytest.fixture(
    autouse=True,
)
def mock_save_file():
    """Mock save_file to return a mock file"""
    with patch("myning.utils.file_manager.FileManager.save") as mock_save_file:
        yield mock_save_file
