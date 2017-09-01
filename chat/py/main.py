import os
import datetime
import atexit
import json
import uuid
import base64

import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.ioloop
from tornado.options import define, options

import db

define("port", default=8000, help="run on the given port", type=int)
define("debug", default=False, help="debug mode", type=bool)

log = db.LogDB()
if not log.check_exist():
    log.create()
atexit.register(log.close)

user_db = db.UserDB()
if not user_db.check_exist():
    user_db.create()
atexit.register(user_db.close)


def log_to_json(content):
    return json.dumps({
        id: {
            "msg": "<br/>".join(msg.split("\n")),
            "display_id" : display_id,
            "post_time": post_time
        }  for id, msg, display_id, post_time in content
    })


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        user_id = self.get_secure_cookie("user_id")
        if not user_id or not user_db.get_display_id(user_id):
            user_id = uuid.uuid4().bytes
            self.set_secure_cookie("user_id", user_id)
            display_id = base64.b16encode(user_id).decode()[:5]
            now = datetime.datetime.now()
            registration_time = now.strftime("%Y-%m-%d %H:%M:%S")
            user_db.insert(user_id, display_id, registration_time)
        self.render("index.html")


class SocketHandler(tornado.websocket.WebSocketHandler):
    users = set()

    def open(self):
        self.users.add(self)
        dumped = log_to_json(log.select_all())
        self.write_message(dumped)

    def on_message(self, message):
        user_id = self.get_secure_cookie("user_id")
        display_id = user_db.get_display_id(user_id)

        msg_json = json.loads(message)
        if msg_json["command"] == "clean":
            log.drop()
            log.create()
            for user in self.users:
                user.write_message("")
            return
            
        now = datetime.datetime.now()
        post_time = now.strftime("%Y-%m-%d %H:%M:%S")
        msg = msg_json["msg"]
        log.insert(msg, display_id, post_time)
        dumped = log_to_json(log.select_all())

        for user in self.users: 
            user.write_message(dumped)

    def on_close(self):
        self.users.remove(self)


if __name__ == "__main__":
    tornado.options.parse_command_line()

    settings = {
        # change own cookie secret by
        # base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
        "cookie_secret" : 'C66jH7QYQ020dgQ6DG9yKNbhWW0ixU/srIqHHh6Mh6g=',
        "debug" : options.debug,
    }
    application = tornado.web.Application([
        (r"/", IndexHandler),
        (r"/ws", SocketHandler),
        ],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        **settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
