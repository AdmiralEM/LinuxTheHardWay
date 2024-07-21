#!/usr/bin/python

# HarvestPackages.py
# 2004 FEB 28 . ccr

# Extract a database of package names, source archives, dependencies,
# and installation procedures from the xml version of the Beyond
# Linux from Scratch book.

# 2004 APR 18 . ccr . Regularize command-line options.

import sys
import os
import optparse
import xml.sax.handler
import PackageDB

ZERO=0
SP=' '
NULL=''
TRUE=1
FALSE=ZERO
NA=-1
QUOTE='"'
APOST="'"
CR=chr(13)
LF='\n'

class cCatalog(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.fResolve={}
        self.fMunge={}
        xml.sax.handler.ContentHandler.__init__(self)
        return
    def setDocumentLocator(self,aLocator):
        self.fLocation=aLocator
        xml.sax.handler.ContentHandler.setDocumentLocator(self,aLocator)
        return
    def startElement(self,aName,aAttrs):

        def GetSafe(aAttrib):
            __Lo=aAttrib.lower()
            for __Attrib in aAttrs.getNames():
                if __Attrib.lower()==__Lo:
                    return aAttrs.getValue(__Attrib)
            return None
        
        if aName.lower() in ['public']:
            self.fResolve[GetSafe('publicId')]=GetSafe('uri')
        elif aName.lower() in ['rewritesystem']:
            self.fMunge[GetSafe('SystemIdStartString')]=GetSafe('rewritePrefix')
        elif aName.lower() in ['rewriteuri']:
            self.fMunge[GetSafe('uriStartString')]=GetSafe('rewritePrefix')
        else:
            pass
        xml.sax.handler.ContentHandler.startElement(self,aName,aAttrs)
        return
    def endElement(self,aName):
        xml.sax.handler.ContentHandler.endElement(self,aName)
        return
    def characters(self,aContent):
        xml.sax.handler.ContentHandler.characters(self,aContent)
        return
    def GetLocSystemId(self):
        return self.fLocation.getSystemId()
    def Resolve(self,aPair):
        (__PublicId,__SystemId)=aPair
        __SystemId=self.fResolve.get(__PublicId,__SystemId)
        for __Prefix in self.fMunge.keys():
            if __SystemId.startswith(__Prefix):
                __SystemId=__SystemId.replace(__Prefix,self.fMunge[__Prefix])
        aPair=(__PublicId,__SystemId)
        return aPair

class cStack(object):
    def __init__(self):
        self.fList=[]
        return
    def Push(self,aItem):
        self.fList.append(aItem)
        return
    def Pop(self):
        return self.fList.pop()
    def GetDepth(self):
        return len(self.fList)
    def IsMostRecently(self,aList,aIgnoreCase=True):

        def Test(aDepth):
            if aIgnoreCase:
                return (aList[-aDepth].lower()==self.fList[-aDepth].lower())
            else:
                return (aList[-aDepth]==self.fList[-aDepth])
        
        __Depth=len(aList)
        if __Depth<=self.GetDepth():
            __Result=Test(__Depth)
            while (__Depth>1) and __Result:
                __Depth=__Depth-1
                __Result=Test(__Depth)
            return __Result
        else:
            return False

class cBook(xml.sax.handler.ContentHandler):
    def __init__(self,aPackageList):
        self.fPackageList=aPackageList
        self.fEltStack=cStack()
        self.fBuffer=NULL
        self.fPackageName=NULL
        self.fPackageVersion=NULL
        self.fURL=NULL
        self.fExternal=NULL
        self.fPackage=None
        self.fCapture=False
        xml.sax.handler.ContentHandler.__init__(self)
        return
    def setDocumentLocator(self,aLocator):
        self.fLocation=aLocator
        xml.sax.handler.ContentHandler.setDocumentLocator(self,aLocator)
        return
    def startElement(self,aName,aAttrs):
        self.ProcessElement(aName,'init',aAttrs)
        return
    def endElement(self,aName):
        self.ProcessElement(aName,'term')
        return
    def ProcessElement(self,aName,aFunction,aAttrs=None):

        def GetSafe(aAttrib):
            __Lo=aAttrib.lower()
            for __Attrib in aAttrs.getNames():
                if __Attrib.lower()==__Lo:
                    return aAttrs.getValue(__Attrib)
            return None
        def Buffer(aIsInit):
            self.fCapture=aIsInit
            if self.fCapture:
                self.fBuffer=NULL
            return
        def PushElement(aIsInit):
            if aIsInit:
                self.fEltStack.Push(aName)
                xml.sax.handler.ContentHandler.startElement(self,aName,aAttrs)
            return
        def PopElement(aIsInit):
            if not aIsInit:
                if self.fEltStack.IsMostRecently([aName]):
                    self.fEltStack.Pop()
                else:
                    sys.stderr.write('''
Element stack corrupted.",aName,"closing but not most recent.
Stack unchanged.
''')
            return
        def ProcessSect1(aIsInit):
            if aIsInit:
                self.fPackageName=GetSafe('id')
                self.fPackageVersion=GetSafe('xreflabel')
            else:
                if self.fPackage==None:
                    pass
                else:
                    self.fPackageList.Append(self.fPackage)
                    self.fPackage=None
            return
        def ProcessTitle(aIsInit):
            Buffer(aIsInit)
            if not aIsInit:
                self.fTitle=self.fBuffer
                if self.fPackageVersion in [NULL,None]:
                    self.fPackageVersion=self.fTitle
            return
        def ProcessPackage(aIsInit):
            if not aIsInit:
                if self.fTitle.lower().startswith('package information'):
                    if self.fPackage==None:
                        self.fPackage=PackageDB.cPackage()
                        self.fPackage.SetNameVersion(self.fPackageName,
                                                     self.fPackageVersion)
                        if OPTS.Verbose==True:
                            sys.stderr.write(self.fPackage.GetNameVersion()+LF)
            return
        def ProcessURL(aIsInit):
            if aIsInit:
                self.fURL=GetSafe('url')
            else:
                if self.fPackage==None:
                    pass
                else:
                    if self.fTitle.lower().startswith('package information'):
                        if self.fURL==NULL:
                            pass
                        else:
                            self.fPackage.fArchiveList=[self.fURL]
                    elif self.fTitle.lower().startswith(
                        'additional download'):
                        self.fPackage.AppendPatch(self.fURL)
            return
        def ProcessConjunction(aIsInit):
            if self.fTitle.lower().startswith('required') or \
                   self.fTitle.lower().startswith('recommended'):
                Buffer(aIsInit)
                if aIsInit:
                    pass
                else:
                    __Tokens=[__Tok.lower() for __Tok in self.fBuffer.split()]
                    if 'or' in __Tokens:
                        self.fPackage.AppendDependency('or')
            return
        def ProcessExternal(aIsInit):
            if aIsInit:
                self.fExternal=GetSafe('linkend')
            else:
                if self.fTitle.lower().startswith('required') or \
                       self.fTitle.lower().startswith('recommended'):
                    if self.fPackage==None:
                        pass
                    else:
                        self.fPackage.AppendDependency(self.fExternal)
            return
        def ProcessForeign(aIsInit):
            Buffer(aIsInit)
            if not aIsInit:
                if self.fTitle.lower().startswith('required') or \
                       self.fTitle.lower().startswith('recommended'):
                    if self.fPackage==None:
                        pass
                    else:
                        self.fPackage.AppendDependency(self.fBuffer)
            return
        def ProcessCode(aIsInit):
            Buffer(aIsInit)
            if not aIsInit:
                if self.fPackage==None:
                    pass
                else:
                    self.fPackage.AppendCommand('# %s\n%s' % \
                                                (self.fTitle,self.fBuffer))
            return

        __IsInit=aFunction in ['init']
        PushElement(__IsInit)
        if self.fEltStack.IsMostRecently(['sect1']):
            ProcessSect1(__IsInit)
        elif self.fEltStack.IsMostRecently(['title']):
            ProcessTitle(__IsInit)
            if self.fEltStack.IsMostRecently(['sect3','title']):
                ProcessPackage(__IsInit)
        elif self.fEltStack.IsMostRecently(['sect3','itemizedlist',
                                            'listitem','para','ulink']):
            ProcessURL(__IsInit)
        elif self.fEltStack.IsMostRecently(['sect4','para']):
            ProcessConjunction(__IsInit)
        elif self.fEltStack.IsMostRecently(['sect4','para','xref']):
            ProcessExternal(__IsInit)
        elif self.fEltStack.IsMostRecently(['sect4','para','ulink']):
            ProcessForeign(__IsInit)
        elif self.fEltStack.IsMostRecently(['screen','userinput']):
            ProcessCode(__IsInit)
        PopElement(__IsInit)
        xml.sax.handler.ContentHandler.endElement(self,aName)
        return
    def characters(self,aContent):
        if self.fCapture:
            self.fBuffer=self.fBuffer+aContent
        xml.sax.handler.ContentHandler.characters(self,aContent)
        return
    def GetLocSystemId(self):
        return self.fLocation.getSystemId()

class cEnts(xml.sax.handler.EntityResolver):
    def __init__(self,aCatalog,aContentHandler):
        self.fCatalog=aCatalog
        self.fContentHandler=aContentHandler
        return
    def resolveEntity2(self,aPublicId,aSystemId,aBase=None):

#       expatreader.py in xml/sax (or PyXML) requires a one-line patch
#       to the external_entity_ref method of the ExpatParser class to
#       provide the third argument.
        
        __Pair=(aPublicId,aSystemId)
        __Pair=self.fCatalog.Resolve(__Pair)
        (aPublicId,aSystemId)=__Pair
        if aSystemId.lower().startswith('file://'):
            aSystemId=aSystemId[7:]
        if aBase==None:
            aBase=self.fContentHandler.GetLocSystemId()
        __Path=os.path.dirname(aBase)
        aSystemId=os.path.join(__Path,aSystemId)
        return xml.sax.handler.EntityResolver.resolveEntity(self,
            aPublicId,aSystemId)

# Mainline begins here..

__Parser=optparse.OptionParser()
__DefaultIndexDoc=os.path.join(os.environ['HOME'],'BLFS/BOOK/index.xml')
__Parser.add_option('-I','--IndexDoc',
                    help='Root of the XML document.  Default is %s.' % (__DefaultIndexDoc),
                    default=__DefaultIndexDoc)
__Parser.add_option('-P','--PackageDB',
                    help='Output file name to receive package database.  Default is > stdout.')
__Parser.add_option('-V','--Verbose',
                    action='store_true',
                    help='List package names during processing.',
                    default=False)
(OPTS,__Args)=__Parser.parse_args()
if len(__Args)>ZERO:
    __Parser.error('Arguments are prohibited.')
if os.path.exists(OPTS.IndexDoc):
    pass
else:
    __Parser.error(OPTS.IndexDoc+' not found.')
if OPTS.PackageDB in [None,NULL,'> stdout']:
    OPTS.PackageDB=None

DOCBOOK_CATALOG='/etc/xml/docbook'

__Catalog=cCatalog()
__Read=xml.sax.make_parser()
__Read.setFeature('http://xml.org/sax/features/external-parameter-entities',False)
__Read.setFeature('http://xml.org/sax/features/external-general-entities',False)
__Read.setContentHandler(__Catalog)
try:
    __Read.parse(DOCBOOK_CATALOG)
except xml.sax._exceptions.SAXParseException:
    sys.stderr.write('Docbook catalog (%s) is illegible.\n' % (DOCBOOK_CATALOG))

__Book=cBook(PackageDB.PackageList)
__Ents=cEnts(__Catalog,__Book)
__Read=xml.sax.make_parser()
__Read.setContentHandler(__Book)
__Read.setEntityResolver(__Ents)
#try:
__Read.parse(OPTS.IndexDoc)
#except xml.sax._exceptions.SAXParseException:
#    sys.stderr.write('XML document (%s) is illegible.\n' % (OPTS.IndexDoc))

PackageDB.Store(OPTS.PackageDB)

# Fin
