from flask import render_template
from flask.views import View


class WebResource(View):
    def dispatch_request(self):
        title = "UMA OCR"
        return render_template('index.html', title=title)
