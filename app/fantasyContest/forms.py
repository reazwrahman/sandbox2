from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired
from wtforms import ValidationError


class ActviveContestantsForm(FlaskForm): 
    
    user_selection = SelectField(u'View the Squad of: ')
    submit = SubmitField('Next')  

######## ------------------------------------------------------####


