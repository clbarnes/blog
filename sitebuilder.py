#!/usr/bin/env python
import sys
from flask import Flask, render_template, render_template_string, Markup
from flask_flatpages import FlatPages, pygmented_markdown
from flask_frozen import Freezer
from YTCrawl import crawler
import csv
from StringIO import StringIO
import datetime as dt


DEBUG = True
# FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.md'

app = Flask(__name__)
app.config.from_object(__name__)
pages = FlatPages(app)
freezer = Freezer(app)

@app.route('/')
def index():
    return render_template('index.html', pages=pages)


@app.route('/<path:path>/')
def page(path):
    page = pages.get_or_404(path)
    return render_template('page.html', page=page)


@app.route('/tag/<string:tag>/')
def tag(tag):
    tagged = [p for p in pages if tag in p.meta.get('tags', [])]
    return render_template('tag.html', pages=tagged, tag=tag)

@app.route('/yt_data/<string:vid_id>/')
def yt_data(vid_id):
    c = crawler.Crawler()
    try:
        results = c.single_crawl(vid_id)
    except Exception, e:
        return str(e)

    headers = ['date', 'dailyViewcount'] + [item for item in ['numShare', 'numSubscriber'] if
                                     results.get(item, False)]

    date = results['uploadDate']
    outstrIO = StringIO()
    writer = csv.writer(outstrIO, delimiter=',')
    writer.writerow(headers)
    for i, count in enumerate(results['dailyViewcount']):
        row = [date.strftime('%Y-%m-%d'), count] + [results[header][i] for header in headers[2:]]
        writer.writerow(row)
        date += dt.timedelta(1)

    raw_str = outstrIO.getvalue()
    print(raw_str)
    return raw_str.replace('\n', '<br />')

def prerender_jinja(text):
    prerendered_body = render_template_string(Markup(text))
    return pygmented_markdown(prerendered_body)

app.config['FLATPAGES_HTML_RENDERER'] = prerender_jinja


if __name__ == '__main__':
    # c = crawler.Crawler()
    # results = c.single_crawl('CleR2nYASdo')
    # print results
    # print len(results['dailyViewcount'])
    if len(sys.argv) > 1 and sys.argv[1] == 'build':
        freezer.freeze()
    else:
        app.run(port=8000, host='0.0.0.0')
