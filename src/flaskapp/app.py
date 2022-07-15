from flask import Flask, request, render_template
from flask_wtf import FlaskForm
from wtforms import FileField, SelectField, SubmitField
from ..restorer.recorder import Recorder

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'a really really really really long secret key'
app.config['UPLOAD_FOLDER'] = 'upload'


class SelectInvalidForm(FlaskForm):
    rec: Recorder = Recorder()
    channel = SelectField(label='Каналы', choices=rec.names)
    submit = SubmitField('Восстановить')


@app.route('/', methods=('GET', 'POST'))
def index():
    form = SelectInvalidForm(csfr_enabled=False)
    if form.validate_on_submit():
        sps, pps = form.rec.parameters(request.form.get('channel'))
        print(f'SPS: {sps} PPS: {pps}')
    return render_template('index.html', form=form)
