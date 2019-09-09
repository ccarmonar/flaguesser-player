"""Player Service"""
from nameko.web.handlers import http
from nameko.rpc import rpc
from player.models import Player, PlayerDatabase
from player.schemas import PlayerSchema
from sqlalchemy import exc


class PlayerService:
    name = "player"

    rep = PlayerDatabase()

    @rpc
    def create_player(self, username, password, country, elo=None):
        try:
            player = Player(username=username, password=password, country=country, elo=elo)
        except AssertionError:
            return False

        try:
            self.rep.db.add(player)
            self.rep.db.commit()
        except exc.IntegrityError:
            self.rep.db.rollback()
            return False

        return True

    @http('POST', '/player')
    def post_player(self, request):
        schema = PlayerSchema(strict=True)
        try:
            player_data = schema.loads(request.get_data(as_text=True)).data
        except ValueError as exc:
            return 400, "Bad request"

        username = player_data['username']
        password = player_data['password']
        country = player_data['country']
        elo = player_data['elo']

        self.create_player(username, password, country, elo)
        return 200, "Ok"

    @rpc
    def get_player_by_username(self, usernm):
        player = self.rep.db.query(Player).filter(Player.username == usernm).first()
        if not player:
            return None
        return PlayerSchema().dump(player).data

    @rpc
    def get_player(self, usernm, passw):
        player = self.rep.db.query(Player).filter(Player.username == usernm).first()
        if not player:
            return None
        if not player.verify_password(passw):
            return None

        return PlayerSchema().dump(player).data

    @rpc
    def update_elo(self, username, delta_elo):
        player_filter = self.rep.db.query(Player).filter(Player.username == username)
        player = player_filter.first()
        player_filter.update({"elo": player.elo + delta_elo})
        self.rep.db.commit()
