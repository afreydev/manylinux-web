from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, validators


class BuildForm(FlaskForm):
    git = StringField('Git repo', [validators.Length(min=20, max=255)])
    python36 = BooleanField('Python 3.6', default=False)
    python37 = BooleanField('Python 3.7', default=False)
    async_build = BooleanField('Async build', [validators.Optional()], default=False)
    submit = SubmitField('Build')

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        result = True
        seen = set()
        fields = [self.python36, self.python37]
        for field in fields:
            if field.data:
                seen.add(field.data)
        if len(seen) < 1:
            for field in fields:
                field.errors.append('Please select at least one version.')
            result = False
        return result
