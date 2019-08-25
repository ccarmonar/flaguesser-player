from sqlalchemy import (
    DECIMAL, Column, DateTime, ForeignKey, Integer, String, LargeBinary
)

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import validates
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

from nameko.extensions import DependencyProvider
from sqlalchemy.orm import sessionmaker, Session


def get_url():
    return (
        "postgresql://{db_user}:{db_pass}@{db_host}:"
        "{db_port}/{db_name}"
    ).format(
        db_user=os.getenv("DB_USER", "postgres"),
        db_pass=os.getenv("DB_PASSWORD", "password"),
        db_host=os.getenv("DB_HOST", "localhost"),
        db_port=os.getenv("DB_PORT", "5432"),
        db_name=os.getenv("DB_NAME", "player"),
    )


DeclarativeBase = declarative_base()


class Player(DeclarativeBase):
    __tablename__ = "Player"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True)
    password = Column(
        EncryptedType(
            String,
            "secret",
            AesEngine,
            "pkcs5"
        )
    )
    country = Column(String(50))
    elo = Column(Integer)
    jwt = Column(LargeBinary(128), nullable=True)

    @validates("username")
    def validate_username(self, key, username):
        assert len(username) > 4
        return username


class PlayerRepository:
    db: Session = None

    def __init__(self, db):
        self.db = db


class PlayerDatabase(DependencyProvider):
    db = None

    def setup(self):
        engine = create_engine(get_url())
        DeclarativeBase.metadata.create_all(engine)
        session = sessionmaker(bind=engine)
        self.db = session()

    def get_dependency(self, worker_ctx):
        return PlayerRepository(self.db)
