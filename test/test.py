import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from nameko.testing.services import worker_factory
from player.service import PlayerService
from player.models import DeclarativeBase, Player, PlayerRepository

import json

TEST_USERNAME = "TestUser"
TEST_USERNAME2 = "TestUser2"
TEST_PASSWORD = "secret"


@pytest.fixture
def session():
    engine = create_engine('sqlite:///:memory:')
    DeclarativeBase.metadata.create_all(engine)

    session_cls = sessionmaker(bind=engine)
    rep = PlayerRepository(session_cls())

    test_player = Player(username=TEST_USERNAME, password=TEST_PASSWORD, country="Chile")
    rep.db.add(test_player)

    return rep


def test_create(session):
    service = worker_factory(PlayerService, rep=session)

    assert not service.create_player(TEST_USERNAME, TEST_PASSWORD, "Chile")
    assert service.create_player(TEST_USERNAME2, TEST_PASSWORD, "Chile")


def test_get_player(session):
    service = worker_factory(PlayerService, rep=session)

    assert service.get_player(TEST_USERNAME, TEST_PASSWORD) is not None
    assert service.get_player(TEST_USERNAME, "") is None

    player = service.get_player_by_username(TEST_USERNAME)
    assert player is not None
    assert service.get_player_by_username("") is None

    assert player["elo"] == 1000

    service.update_elo(TEST_USERNAME, 10)
    player = service.get_player_by_username(TEST_USERNAME)

    assert player["elo"] == 1010
