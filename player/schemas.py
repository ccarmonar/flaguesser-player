from marshmallow import Schema, fields


class PlayerSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    country = fields.Str()
    elo = fields.Integer(default=0)