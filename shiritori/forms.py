from flask.ext.wtf import Form
from wtforms import StringField,IntegerField
from wtforms.validators import InputRequired


class GameForm(Form):
    word = StringField('Kelime',validators=[InputRequired()])

class CreateForm(Form):
    id = IntegerField('id',validators=[InputRequired()])