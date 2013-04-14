import subprocess
import os
import time
import tempfile
import re

import ovalidentifiers

class SSGGit:
    def __init__(self, path):
        self.cwd = os.path.dirname(os.path.realpath(__file__))
        self.ssggit = 'git://git.fedorahosted.org/git/scap-security-guide.git'
        self.path = path
        self.timeout = 60 # minimal git pull inteval
        self.lastPulled = 0

        self.files = []
        self.xccdf = {}
        self.oval = {}
        self.ovalIds = {}
        self.xccdfDirs = set()
        self.pathPrefix = ''
        self.lastPulled = 0

        if not os.path.exists(self.path):
            self.__clone()
            return

        # the right git repository?
        process = subprocess.Popen(['git', 'config', '--get', 'remote.origin.url'], \
                stdout = subprocess.PIPE, stderr = subprocess.PIPE, cwd = self.path)
        (stdout, stderr) = process.communicate()

        if (process.returncode != 0 or stdout.find(self.ssggit) < 0):
            self.__clone()
            return

        self.getFiles()
        self.pull()

    def __clone(self):
        print 'cloning scap-secutiry-guide git, this will take a while'
        process = subprocess.Popen(['git', 'clone', self.ssggit, self.path], \
                stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        (stdout, stderr) = process.communicate()

        if (process.returncode != 0):
            print ('git clone failed')
            print stderr + stdout
            return

        self.lastPulled = time.time()
        self.getFiles()
        print 'git clone complete'

    def make(self, path = None):
        if (path == None):
            process = subprocess.Popen(['make'], stdout = subprocess.PIPE, \
                    stderr = subprocess.PIPE, cwd = self.path)
        else:
            process = subprocess.Popen(['make'], stdout = subprocess.PIPE, \
                    stderr = subprocess.PIPE, cwd = path)

        (stdout, stderr) = process.communicate()
        return (process.returncode, stderr + stdout)

    def pull(self):
        if (time.time() < self.lastPulled + self.timeout):
            return

        process = subprocess.Popen(['git', 'pull'], stdout = subprocess.PIPE, \
                stderr = subprocess.PIPE, cwd = self.path)
        (stdout, stderr) = process.communicate()

        if (process.returncode != 0):
            print ('git pull failed')
            print stderr + stdout
            return

        self.lastPulled = time.time()
        if (stdout.find('up-to-date') < 0):
            self.getFiles()
    
    def getFiles(self):
        self.__getXccdfFiles()
        self.__getOvalFiles()
        self.__getOvalIds()

    def __getXccdfFiles(self):
        # TODO Jboss
        for (root, dirs, files) in os.walk(self.path):
            if (root.find('input') < 0 or root.find('rpmbuild') >= 0 or 
                    root.find('checks') >= 0):
                continue

            (product, path) = self.productPath(root)
            if not product in self.xccdf.keys():
                self.xccdf[product] = []

            for f in files:
                fullpath = os.path.join(root, f)
                if (os.path.splitext(f)[1] != '.xml'):
                    continue

                splitted = fullpath.split('/')
                for i in range(0, len(splitted)):
                    if (splitted[i] == 'input'):
                        break

                self.xccdf[product].append(fullpath)
                self.files.append(fullpath)

                self.pathPrefix = '/'.join(splitted[0:i-1])

                # don't let users create new files directly in input/ directory
                if (i > len(splitted) - 3):
                    continue
                self.xccdfDirs.add('/'.join(splitted[i-1:-1]))

    def diff(self, filename, content):
        self.modify(filename, content)

        if not filename in self.files:
            process = subprocess.Popen(['git', 'add', '/'.join(filename.split('/')[1:])], \
                    stdout = subprocess.PIPE, stderr = subprocess.PIPE, \
                    cwd = self.path)
            process.communicate()

            process = subprocess.Popen(['git', 'diff', 'HEAD'], \
                    stdout = subprocess.PIPE, stderr = subprocess.PIPE, \
                    cwd = self.path)
            (stdout, stderr) = process.communicate()

        else:
            process = subprocess.Popen(['git', 'diff', '-w'], \
                    stdout = subprocess.PIPE, stderr = subprocess.PIPE, \
                    cwd = self.path)
            (stdout, stderr) = process.communicate()

        self.undo(filename)
        return stdout + stderr

    def modify(self, filename, content):
        fh = open(os.path.join(self.cwd, filename), 'w+')
        fh.write(content)
        fh.close()

        if (not filename in self.files) and (filename.find('checks') < 0):
            self.modifyGuideXslt(filename)

    def modifyGuideXslt(self, filename):
        splitted = filename.split('/')
        for i in range(0, len(splitted)):
            if (splitted[i] == 'input'):
                break
        name = '/'.join(splitted[i + 1 : ])
        path = '/'.join(splitted[i + 1 : -1])
        xslt = '/'.join(splitted[: i + 1]) + '/guide.xslt'

        fh = open(os.path.join(self.cwd, xslt), 'r')
        lines = fh.readlines()
        fh.close()

        rightLine = re.compile("[^$]+" + path + "/[^/]+.xml*")
        # walk through xslt lines backwards
        for i in range(len(lines) - 1, 0, -1):
            if (rightLine.match(lines[i])):
                break

        replacer = re.compile(path + "/[^/]+.xml")
        lines.insert(i + 1, replacer.sub(name, lines[i]))
        
        fh = open(os.path.join(self.cwd, xslt), 'w')
        fh.write(''.join(lines))
        fh.close()


    def undo(self, filename):
        if not filename in self.files:
            process = subprocess.Popen(['git', 'reset', 'HEAD', '.'], cwd = self.path)
            process.communicate()
            process = subprocess.Popen(['rm', '-f', filename]) 
            process.communicate()

        process = subprocess.Popen(['git', 'checkout', '--', '.'], cwd = self.path)
        process.communicate()

    def delete(self, file):
        process = subprocess.Popen(['rm',  file])
        process.communicate()

        process = subprocess.Popen(['git', 'diff'], \
                stdout = subprocess.PIPE, stderr = subprocess.PIPE, \
                cwd = self.path)
        (stdout, stderr) = process.communicate()

        process = subprocess.Popen(['git', 'checkout', '--', '.'], cwd = self.path)
        process.communicate()

        return stdout + stderr

    def fileContent(self, filename):
        f = open(os.path.join(self.cwd, filename))
        text = f.read()
        f.close()
        return text

        return 'File not found in git'

    def productPath(self, filename):
        splitted = filename.split('/')
        for i in range(0, len(splitted)):
            if (splitted[i] == 'input'):
                break
        product = splitted[i - 1]
        path = '/'.join(splitted[:i])

        return (product, path)

    def productXccdf(self, product):
        return self.pathPrefix + '/' + product + '/output/ssg-' + product.lower() + '-xccdf.xml'

    def productOval(self, product):
        return self.pathPrefix + '/' + product + '/output/ssg-' + product.lower() + '-oval.xml'

    def __getOvalFiles(self):
        for (root, dirs, files) in os.walk(self.path):
            if (root.find('input') < 0 or root.find('rpmbuild') >= 0 or 
                    root.find('checks') < 0):
                continue

            (product, path) = self.productPath(root)
            if not product in self.oval.keys():
                self.oval[product] = []

            for f in files:
                fullpath = os.path.join(root, f)
                splitted = fullpath.split('/')
                if ((os.path.splitext(f)[1] != '.xml') or
                    (splitted[len(splitted) - 2] != 'checks')):
                    continue

                self.oval[product].append(fullpath)
                self.files.append(fullpath)

    def getOvalDirs(self):
        result = []

        for product in self.oval.keys():
            result.append(product + '/input/checks')
            
        return result

    def __getOvalIds(self):
        idGetter = ovalidentifiers.OvalIds()

        for product in self.oval.keys():
            self.ovalIds[product] = []
            for file in self.oval[product]:
                self.ovalIds[product].append(idGetter.getIdsFromFile(file))

