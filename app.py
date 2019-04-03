from common import get_email_content
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    output = get_email_content()
    if len(output) == 0:
        return 'Nothing today :('

    output += '<style type="text/css">'
    output += 'body { font-family: Helvetica; font-size: 13px }'
    output += '</style>'

    return output

if __name__ == '__main__':
    app.run()
