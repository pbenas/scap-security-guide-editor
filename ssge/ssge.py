#!/usr/bin/env python

from flask import Flask, render_template, request, url_for, Response, redirect
from werkzeug import secure_filename
import os.path
import json
import sys

from xsdparser import XsdParser
from validator import Validator
from formatrecognizer import FormatRecognizer
from ssggit import SSGGit
from ovalparser import OvalParser

myValidator = Validator()
recognizer = FormatRecognizer()
xccdfParser = XsdParser()
ovalParser = OvalParser()
git = SSGGit(os.path.expanduser('~/.scap-security-guide-git'))

templates =  os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')
static =  os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')
app = Flask(__name__, template_folder = templates, static_folder = static)

@app.route('/', methods=['GET', 'POST'])
def modeSelector():
    if request.method == 'POST':
        if ('xccdfStart' in request.form.keys()):
            xccdffile = request.form['xccdffile']
            return editor(git.fileContent(xccdffile), xccdffile, True, 'xccdf')

        elif ('xccdfNew' in request.form.keys()):
            return redirect(url_for('newxccdf'))

        elif ('xccdfDelete' in request.form.keys()):
            return delete(request.form['xccdffile'])

        elif ('ovalStart' in request.form.keys()):
            ovalfile = request.form['ovalfile']
            return editor(git.fileContent(ovalfile), ovalfile, True, 'oval')

        elif ('ovalNew' in request.form.keys()):
            return redirect(url_for('newoval'))

        elif ('ovalDelete' in request.form.keys()):
            return delete(request.form['ovalfile'])

        elif ('upload' in request.form.keys()):
            file = request.files['file']
            content = file.read()
            format = recognizer.recognize(content)
            return editor(content, secure_filename(file.filename), False, format)

    return render_template('modeselector.html', xccdffiles = git.xccdf, ovalfiles = git.oval)

def editor(content, filename, gitfile, format):
    if (format == 'xccdf'):
        xccdfParser.setXsd('http://scap.nist.gov/schema/xccdf/1.2/xccdf_1.2.xsd')
        xccdfParser.parse()
        parser = xccdfParser
    else:
        parser = ovalParser
        if (gitfile):
            # scap security guide project introduces <def-group> tag
            parser.hints['<def-group><'] = parser.hints['<']
            parser.hints['<'] = [{'hint' : 'def-group', 'help' : 'SSG uses OVAL this way.'}]

    if (format == 'xccdf' and gitfile and (filename.find('guide.xml') < 0)):
        shorthand = json.loads(git.fileContent('static/shorthand.json'))
        # add hints for oval IDs
        (product, path) = git.productPath(filename)
        shorthand['<oval id='] = []
        for (id, description) in sorted(git.ovalIds[product]):
            shorthand['<oval id='].append({'hint' : '"' + id + '"', 'help' : description})
        hints = json.dumps(shorthand) + ';'
    else:
        hints = json.dumps(parser.hints)

    return render_template('editor.html', content = content, filename = filename, \
            download = url_for('download'), hints = hints, gitfile = gitfile, format = format)

def delete(file):
    result = git.delete(file)
    def generate():
        yield result
    return Response(generate(), mimetype = 'text/x-patch', headers = {'Content-Disposition':
            'attachment;filename=' + file + '.patch' })


@app.route('/download', methods=['POST'])
def download():
    if 'patch' in request.form.keys():
        result = git.diff(request.form['filename'], request.form['myTextarea'])
        mimetype = 'text/x-patch'
        (dir, file) = os.path.split(request.form['filename'])
        filename =  file + '.patch'
    else:
        result = request.form['myTextarea']
        mimetype = 'application/xml'
        filename = request.form['filename']

    def generate():
        yield result
    return Response(generate(), mimetype = mimetype, headers = {'Content-Disposition':
            'attachment;filename=' + filename })

@app.route('/validate', methods=['POST'])
def validate():
    if request.form['gitfile'] == 'no':
        return myValidator.validateUserFile(request.form.get('text', '', type=str), 
                request.form['format'])
    else:
        git.modify(request.form['filename'], request.form['text'])
        (product, path) = git.productPath(request.form['filename'])
        errors = ''
        (ret, err) = git.make(path)
        for line in err.split('\n'):
            if (line.find('error') >= 0):
                errors += line + '\n'

        git.undo(request.form['filename'])

        if (ret != 0):
            return 'Make failed: ' + err

        if (errors != ''):
            return 'Errors found in make output : ' + err

        if (request.form['format'] == 'xccdf'):
            return myValidator.validateUserFile(git.fileContent(git.productXccdf(product)),
                'xccdf')
        else:
            return myValidator.validateUserFile(git.fileContent(git.productOval(product)),
                'oval')

@app.route('/newxccdf', methods=['GET', 'POST'])
def newxccdf():
    return newfile(format = 'xccdf')

@app.route('/newoval', methods=['GET', 'POST'])
def newoval():
    return newfile(format = 'oval')

def newfile(format = 'xccdf'):
    if request.method == 'POST':
        dir = request.form['dir']
        filename = request.form['filename']
        pos = filename.find('.xml')
        if (pos < 0):
            name = filename
        else:
            name = filename[0:pos]

        if (request.form['format'] == 'xccdf'):
            format = 'xccdf'
        else:
            format = 'oval'

        return editor(render_template(format + '.xml', name = name), 
                git.pathPrefix + '/' + dir + '/' + filename, gitfile = True, format = format)

    if (format == 'xccdf'):
        return render_template('newfile.html', dirs = git.xccdfDirs, format = 'xccdf')
    else:
        return render_template('newfile.html', dirs = git.getOvalDirs(), format = 'oval')


if __name__ == '__main__':
    if (len(sys.argv) == 2 and (sys.argv[1].find('--debug') >= 0)):
        app.run(port = 4444, debug = True)
    else:
        app.run(port = 4444, host = '0.0.0.0', debug = False)
# debug mode brings risk of remote code execution, limit application visibility 
# to localhost only in debug mode

