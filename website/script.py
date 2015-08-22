# -*- coding: utf-8 -*-

from website import db
from website import models
from flask.ext.script import Command


class ResetDB(Command):
    """Drops all tables and recreates them"""

    def run(self, **kwargs):
        self.drop_collections()

    @staticmethod
    def drop_collections():
        db.drop_all()
        db.create_all()


class PopulateDB(Command):
    """Fills in predefined data to DB"""

    def run(self, **kwargs):
        self.create_roles()
        self.create_users()
        self.create_news()

    @staticmethod
    def create_roles():
        for role in ('admin', 'end-user', 'author'):
            models.user_datastore.create_role(name=role, description=role)
        models.user_datastore.commit()

    @staticmethod
    def create_users():
        for u in (('admin', 'admin@admin.com', '123456', ['admin'], True),
                  ('user', 'user@user.com', '123456', ['end-user'], True),
                  ('lavasystem', 'lava@lava.com', '123456', ['admin'], True),
                  ('tiya', 'tiya@lp.com', '123456', [], False)):
            user = models.user_datastore.create_user(
                username=u[0],
                email=u[1],
                password=u[2],
                roles=u[3],
                active=u[4]
            )

            models.user_datastore.commit()



if __name__ == "__main__":
    ResetDB.drop_collections()
    PopulateDB.create_roles()
    PopulateDB.create_users()
