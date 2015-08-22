from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin import Admin
from flask.ext.security import current_user,utils
from website import db
from website.models import User, Role
from wtforms.fields import TextField


class AdminModelView(ModelView):
    # Prevent administration of Users unless the currently logged-in user has the "admin" role
    def is_accessible(self):
        return current_user.has_role('admin')

class UserModelView(AdminModelView):
    # On the form for creating or editing a User, don't display a field corresponding to the model's password field.
    # There are two reasons for this. First, we want to encrypt the password before storing in the database. Second,
    # we want to use a password field (with the input masked) rather than a regular text field.
    def scaffold_form(self):

        # Start with the standard form as provided by Flask-Admin. We've already told Flask-Admin to exclude the
        # password field from this form.
        form_class = super(UserModelView, self).scaffold_form()

        # Add a password field, naming it "password2" and labeling it "New Password".
        form_class.password2 = TextField('New Password')
        return form_class

    # This callback executes when the user saves changes to a newly-created or edited User -- before the changes are
    # committed to the database.
    def on_model_change(self, form, model, is_created):

        # If the password field isn't blank...
        if len(model.password2):

            # ... then encrypt the new password prior to storing it in the database. If the password field is blank,
            # the existing password in the database will be retained.
            model.password = utils.encrypt_password(model.password2)

def init_admin(app):
    admin = Admin(app)
    admin.add_view(UserModelView(User, db.session, category='Auth'))
    admin.add_view(AdminModelView(Role, db.session, category='Auth'))