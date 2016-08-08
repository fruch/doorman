import datetime
import json

import pymongo.errors
from bson import json_util
import pymongo
import pql
from flask import Flask, request, g
from flask_restful import Resource, Api, reqparse, abort

app = Flask(__name__)
api = Api(app)

app.config.from_pyfile('config.py', silent=True)


def get_resources_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'resources'):
        g.resources = pymongo.MongoClient(app.config['MONGO_URL']).db.resources
        g.resources.ensure_index('id', unique=True)

    return g.resources

post_parser = reqparse.RequestParser()
post_parser.add_argument(
    'username', dest='username',
    required=True,
    help='The user\'s username',
)
post_parser.add_argument(
    'resource', dest='resource',
    required=False,
    help='The resource to lock',
)
post_parser.add_argument(
    'duration', dest='duration',
    help="for how much time the resource will be saved"
)
post_parser.add_argument(
    'q', dest='query',
    required=False,
    help='query to use',
)


query_parser = reqparse.RequestParser()
query_parser.add_argument(
    'q', dest='query',
    required=False,
    help='query to use',
)

class LockedResource(Resource):
    @staticmethod
    def put(id):
        resources = get_resources_db()
        try:
            obj = resources.insert(dict(id=id, data = request.get_json()))
            obj = resources.find_one(dict(id=id))
            return json.loads(json.dumps(obj, sort_keys=True, indent=4, default=json_util.default))
        except pymongo.errors.DuplicateKeyError:
            abort(405, message="key[%s] already in use" % id)

    @staticmethod
    def patch(id):
        resources = get_resources_db()

        obj = resources.update_one(dict(id=id),
                                   {"$set":
                                        dict({"data.%s" % k : v for k, v in request.get_json().items()})
                                   })

        obj = resources.find_one(dict(id=id))
        if not obj:
            abort(404, message="%s not found" % id)
        return json.loads(json.dumps(obj, sort_keys=True, indent=4, default=json_util.default))

    @staticmethod
    def get(id):
        resources = get_resources_db()

        obj = resources.find_one(dict(id=id))
        return json.loads(json.dumps(obj, sort_keys=True, indent=4, default=json_util.default))

    @staticmethod
    def delete(id):
        resources = get_resources_db()

        obj = resources.remove(dict(id=id))
        if obj['n'] < 1:
            abort(404, message="key[%s] wasn't found" % id)
        return "deleted"


class LockedResourceList(Resource):
    def get(self):
        resources = get_resources_db()

        args = query_parser.parse_args()
        if args.query:
            q = pql.find(args.query)
        else:
            q = None
        objs = resources.find(q)
        objs = [o for o in objs]
        if not objs:
            abort(404, message="'%s' wasn't found" % args.query)
        return json.loads(json.dumps(objs, sort_keys=True, indent=4, default=json_util.default))


class Lock(Resource):
    @staticmethod
    def post():
        resources = get_resources_db()

        args = post_parser.parse_args()
        if args.query:
            query = pql.find(args.query)
        else:
            query = dict(id=args.resource)
        obj = resources.find_one(query)
        if not obj:
            abort(404, message="resource[%s] wasn't found" % args.resource)
        if obj.get('locked_by', None):
            abort(405, message="locked by %s" % obj['locked_by'])
        duration = args.duration if args.duration else 0
        lock_endtime = datetime.datetime.now() + datetime.timedelta(minutes=duration)
        res = resources.update_one({'_id': obj['_id']}, {"$set": {'locked_by': args.username, 'lock_end': lock_endtime}})
        obj = resources.find_one(dict(id=args.resource))

        return json.loads(json.dumps(obj, sort_keys=True, indent=4, default=json_util.default))

    @staticmethod
    def delete(id):
        resources = get_resources_db()
        obj = resources.find_one(dict(id=id))
        if not obj:
            abort(404, message="resource[%s] wasn't found" % id)
        if obj.get('locked_by', None):
            res = resources.update_one({'_id': obj['_id']}, {"$unset": {'locked_by': '', 'lock_end': ''}})
            obj = resources.find_one(dict(id=id))
            return json.loads(json.dumps(obj, sort_keys=True, indent=4, default=json_util.default))
        else:
            abort(404, message="resource[%s] is not locked" % id)


api.add_resource(LockedResourceList, '/resources')
api.add_resource(LockedResource, '/resource/<string:id>')
api.add_resource(Lock, '/lock', '/lock/<string:id>')
