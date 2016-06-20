# all the imports
from __future__ import with_statement
from flask import Flask, request, redirect, url_for, render_template
import functions


DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


iq = ""
cq = ""
new_chars = []


@app.route('/')
def show_result():
    iq = request.args['iq'] if 'iq' in request.args else ''
    
    newresults, new_chars = functions.checkGramma(iq);
    return render_template('show_result.html', output=new_chars, inputquery=iq, changequery = newresults)

@app.route('/search', methods=['POST'])
def search_entry():
    iq = request.form['text']
    return redirect(url_for('show_result', iq=iq))

if __name__ == '__main__':
    app.run()
