#!/usr/bin/env python

##############################################################################
# Utility for Cuckoo
#    You can get from here http://ge.tt/5aiVXAP
#    or visit to http://ickhyun82.blogspot.kr/2012/04/mac.html
# 
# This program is used for exporting readable file format from raw file that
# collected by Cuckoo.
# 
# 2012. 12. 5. 
# contact me at ickhyun82@gmail.com
##############################################################################

from os.path import expanduser
import sys
import glob
import re
import inspect

from optparse import OptionParser

rawFileName = '.cuckoo_history.*'
extFormat = 'YYYYMM'
homeDir = expanduser('~')

rawFileNameList = glob.glob('%s/%s' % (homeDir, rawFileName))

def getRawText():
    fullText = ''
    for rawFile in rawFileNameList:
        try:
            fd = open(rawFile, 'r')
            fullText += fd.read()
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
        else:
            fd.close()

    return fullText

def finditer(text):
    pattern = re.compile('^\?(.+?)\?', re.MULTILINE|re.DOTALL)
    return re.finditer(pattern, text)

def titleAndDesc(filteredItem, separator='\n'):
    item = filteredItem.group(1).strip().splitlines()
    return item[0].lower(), separator.join(item[1:])

def indexof(bucket, item):
    try:
        return bucket.index(item)
    except ValueError:
        return -1

def hasItem(bucket, item):
    return indexof(bucket, item) > -1

class Formatter:
    def build(self, filteredList):
        raise NotImplementedError


class HTMLFormatter(Formatter):
    alias = 'html'

    def build(self, filteredList):
        for filteredItem in filteredList:
            title, desc = titleAndDesc(filteredItem, separator="<BR/>")
            print "<H3>"
            print title
            print "</H3>"
            print "<P>"
            print desc
            print "</P>"

class ReStructuredTextFormatter(Formatter):
    alias = 'rst'

    def build(self, filteredList):
        for filteredItem in filteredList:
            title, desc = titleAndDesc(filteredItem)
            print title
            print "="*len(title)
            print desc

class FormatterFactory:
    def __init__(self):
        currentClasses = inspect.getmembers(sys.modules[__name__], inspect.isclass)
        self.formatterList = []
        self.usableFormatters = {}
        for m in currentClasses:
            for tree in inspect.getmro(m[1]):
                if Formatter == tree and m[0] != Formatter.__name__:
                    self.formatterList.append(eval(m[0]))

        for formatter in self.formatterList:
            self.usableFormatters[formatter.alias] = formatter()

    def getFormatterAliasList(self):
        return self.usableFormatters.keys()

    def create(self, formatter):
        return self.usableFormatters[formatter]

class Builder:
    def __init__(self, filteredList):
        self.filteredList = filteredList

    def build(self, formatter):
        formatter.build(self.filteredList)

def removeDuplicate(_iter):
    items = []
    for item in _iter:
        title, _ = titleAndDesc(item)
        if(hasItem(items, title)):
            continue
        items.append(title)
        yield item

if __name__ == '__main__':
    factory = FormatterFactory()

    parser = OptionParser(usage="usage: %prog [options] filename",
            version="%prog 1.0")
    parser.add_option("-f", "--format",
            action="store",
            dest="outputFormat",
            choices=factory.getFormatterAliasList(),
            default='rst',
            help='Output file format')

    (options, args) = parser.parse_args()

    matches = finditer(getRawText())
    filteredList = filter(lambda m:len(m.group(1).strip().splitlines()) > 1, matches)
    builder = Builder(removeDuplicate(filteredList))
    builder.build(factory.create(options.outputFormat))

