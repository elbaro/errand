from rq.decorators import job
import redis
import rq_dashboard
import os

redis = redis.Redis(host='localhost', port='6379')

from flask import Flask, request
flask_app = Flask(__name__)
flask_app.config.from_object(rq_dashboard.default_settings)
flask_app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")


@job('print', connection=redis)
def print(sides, url=None, file=None):
    assert sides in ['one-sided', 'two-sided-long-edge', 'two-sided-short-edge']
    if url is not None:
        return os.system('curl -s %s | lpr -o sides=%s' % (url, sides))
    elif file is not None:
        pass
    else:
        return 'nothing to print'


def get_html():
    return '''
        <h1>Prints</h1>
            <form method='post' action='/print'>
                URL: <input type='text' name='url'/><br/>
                File: <input type='file' name='file'/><br/>
                <input type='radio' name='sides' id='s1' value='one-sided' /><label for='s1'>one side</label>
                <input type='radio' name='sides' id='s2' value='two-sided-long-edge' checked /><label for='s2'>two sides, long</label>
                <input type='radio' name='sides' id='s3' value='two-sided-short-edge' /><label for='s3'>two sides, short</label>
                <input type='submit' />
            </form>
            <h2>Recents</h2>
            <table style='border:1;'>
                <tr>
                    <th>Date</th>
                    <th>Who</th>
                    <th>Status</th>
                </tr>
                <tr>
                    <td>1999.09.01</td>
                    <td>username</td>
                    <td>pending</td>
                </tr>
                <tr>
                    <td>1999.09.01</td>
                    <td>username</td>
                    <td>failed</td>
                </tr>
            </table>
    '''


@flask_app.route('/')
def index():
    html = ['<a href="/rq">status</a><hr/>']
    # for h in handlers:
    #     html.append(h.get_html())
    #     html.append('<hr/>')
    # html.append(inspect())
    html.append(get_html())
    html.append('<hr/>')
    html.append('<h1>workers</h1>')
    return ''.join(html)


@flask_app.route('/print', methods=['POST'])
def q_print():
    print(request.form['sides'])
    if request.form['sides'] not in ['one-sided', 'two-sided-long-edge', 'two-sided-short-edge']:
        return 'choose sides'
    if request.form['url'] != '':
        print.delay(url=request.form['url'], sides=request.form['sides'])
        return 'enqueued'
    elif request.form['file'] != '':
        return "doesn't support file print yet"
    else:
        return 'nothing to print'
