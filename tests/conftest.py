"""Pytest conftest file."""

from unittest.mock import patch

import pytest

from myning.objects.game import Game
from myning.objects.player import Player
from myning.objects.trip import Trip

# Initialize objects before app tests
Player.initialize("MockPlayer")
Game.initialize()
Trip.initialize()

# Set up values for tests
player = Player()
game = Game()
trip = Trip()

player.reset()
game._state = 2
trip.clear()


@pytest.fixture(autouse=True)
def mock_save():
    """Mock file save operations"""
    with (
        patch("myning.utilities.file_manager.FileManager.save"),
        patch("myning.utilities.file_manager.FileManager.multi_save"),
    ):
        yield


@pytest.fixture(autouse=True)
def reset_objects():
    player.reset()
    trip.clear()


@pytest.fixture
async def app_and_pilot():
    from myning.tui.app import MyningApp

    app = MyningApp()
    async with app.run_test() as pilot:
        yield app, pilot


@pytest.fixture
def app(app_and_pilot):
    app, _ = app_and_pilot
    yield app


@pytest.fixture
def pilot(app_and_pilot):
    _, pilot = app_and_pilot
    yield pilot
