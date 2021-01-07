
import flask
from flask import current_app
from flask_principal import Identity, identity_changed
from invenio_access import authenticated_user
from marshmallow import ValidationError
from marshmallow import __version_info__ as marshmallow_version


def set_identity(u):
    """Sets identity in flask.g to the user."""
    identity = Identity(u.id)
    identity.provides.add(authenticated_user)
    identity_changed.send(current_app._get_current_object(), identity=identity)
    assert flask.g.identity.id == u.id

def marshmallow_load(schema, data):
    ret = schema.load(data)
    if marshmallow_version[0] >= 3:
        return ret
    if ret[1] != {}:
        raise ValidationError(message=ret[1])
    return ret[0]
