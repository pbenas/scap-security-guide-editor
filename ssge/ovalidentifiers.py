import re

from lxml import etree

class OvalIds:
    def __init__(self):
        pass

    def getIdsFromFile(self, filename):
        f = open(filename)
        text = f.read()
        f.close()

        # remove all namespaces. lxml can't work with unknown namespaces and namespaces are irrelevant
        # for this case

        nspaceStartRemover = re.compile('<\w+:')
        nspaceEndRemover = re.compile('<\/\w+:')
        nspaceAttributeRemover = re.compile(' \w+:')

        text = nspaceStartRemover.sub('<',text)
        text = nspaceEndRemover.sub('</',text)
        text = nspaceAttributeRemover.sub(' ',text)

        root = etree.fromstring(text)
        for elem in root.iter():
            if elem.tag is etree.Comment:
                continue
            # interested only in description tags
            if elem.tag.find('description') < 0:
                continue

            description = elem.text
           
            # parent of description should me <metadata> which parent should be <definition> 
            # carrying the "id" attribute
            id = elem.getparent().getparent().get('id')

            return (id, description)

