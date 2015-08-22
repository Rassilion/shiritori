from flask.ext.script import Manager
from flask.ext.script.commands import Server, Shell, ShowUrls, Clean
from flask.ext.security.script import CreateUserCommand, AddRoleCommand, \
    RemoveRoleCommand, ActivateUserCommand, DeactivateUserCommand

from website import app
from website.script import ResetDB, PopulateDB

manager = Manager(app)
manager.add_command("shell", Shell())
manager.add_command("runserver", Server(use_reloader=True, use_debugger=True))
manager.add_command("show_urls", ShowUrls())
manager.add_command("clean", Clean())

manager.add_command("reset_db", ResetDB())
manager.add_command("populate_db", PopulateDB())

manager.add_command('create_user', CreateUserCommand())
manager.add_command('add_role', AddRoleCommand())
manager.add_command('remove_role', RemoveRoleCommand())
manager.add_command('deactivate_user', DeactivateUserCommand())
manager.add_command('activate_user', ActivateUserCommand())

if __name__ == "__main__":
    manager.run()
