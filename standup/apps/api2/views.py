from collections import OrderedDict

from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import desc
from standup.apps.status.models import Status
from standup.database import get_session


blueprint = Blueprint('api_v2', __name__, url_prefix='/api/v2')


@blueprint.route('/', methods=['GET'])
@blueprint.route('/feed/', methods=['GET'])
def feed():
    """Get all status updates.

    Returns id, user (the name), project name and timestamp of statuses.

    The amount of items to return is determined by the limit argument
    (defaults to 20)::

        /api/v2/feed/?limit=20

    An example of the JSON::

        {
            "1": {
                "user": "r1cky",
                "content": "working on bug 123456",
                "project": "sumodev",
                "timestamp": "2013-01-11T21:13:30.806236"
            }
        }

    """
    db = get_session(current_app)

    limit = request.args.get('limit', 20)

    statuses = db.query(Status).filter_by(reply_to=None)\
        .order_by(desc(Status.created)).limit(limit)

    data = OrderedDict()
    for row in statuses:
        id = row.id
        created = row.created.isoformat()
        if row.project is not None:
            project_name = row.project.name
        else:
            project_name = None
        data[id] = (dict(author=row.user.name, content=row.content,
                         timestamp=created, project=project_name))

    return jsonify(data)
