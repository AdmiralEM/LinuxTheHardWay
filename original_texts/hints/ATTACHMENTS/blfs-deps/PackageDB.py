#!/usr/bin/python

# PackageDB.py
# 2004 MAR 01 . ccr

# This unit contains the cPackage class definition.

# 2004 APR 18 . ccr . Define cFile class.

import sys

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

A_MARGIN=   '        '
B_MARGIN=   '          '
TAG_PACKAGE='Package:  '
TAG_VERSION='Version:  '
TAG_ARCHIVE='Archive:  '
TAG_PATCHES='Patches:  '
TAG_DEPENDS='Depends:  '
TAG_COMMAND='Command:  '

class cPackage(object):
    def __init__(self):
        self.fName=NULL
        self.fVersion=NULL
        self.fArchiveList=[]
        self.fPatchList=[]
        self.fDependsOnList=[]
        self.fInstallCommandList=[]
        return
    def GetKey(self):
        return self.fName
    def GetTitle(self):
        return self.fVersion
    def CountArchives(self):
        return len(self.fArchiveList)
    def CountPatches(self):
        return len(self.fPatchList)
    def CountDependencies(self):
        return len(self.fDependsOnList)
    def GetDependencies(self):
        return self.fDependsOnList
    def CountCommandCodeFragments(self):
        return len(self.fInstallCommandList)
    def GetNameVersion(self):
        return '%s (%s)' % (self.fName,self.fVersion)
    def SetNameVersion(self,aName,aVersion):
#        __Match=re.search('^(.*?)-([0-9\.\-]*)$',aNameVersion)
#        if __Match==None:
#            self.fName=aNameVersion
#            self.fVersion=NULL
#        else:
#            self.fName=__Match.group(1)
#            if self.fName==None:
#                self.fName=aNameVersion
#                self.fVersion=NULL
#            else:
#                self.fVersion=__Match.group(2)
#                if self.fVersion==None:
#                    self.fVersion=NULL
        if aName==None:
            self.fName='--Missing--'
        else:
            self.fName=aName
        if aVersion==None:
            self.fVersion=NULL
        else:
            self.fVersion=aVersion
        return
    def AppendArchive(self,aArchive):
        self.fArchiveList.append(aArchive)
        return
    def AppendPatch(self,aPatch):
        self.fPatchList.append(aPatch)
        return
    def AppendDependency(self,aDep):
        self.fDependsOnList.append(aDep)
        return
    def AppendCommand(self,aCmd):
        self.fInstallCommandList.append(aCmd)
        return
    def Store(self,aUnit):
        aUnit.write(' Name:'+self.fName+LF)
        aUnit.write('  Ver:'+self.fVersion+LF)
        self.StoreList(aUnit,self.fArchiveList,       ' Arch:')
        self.StoreList(aUnit,self.fPatchList,         'Patch:')
        self.StoreList(aUnit,self.fDependsOnList,     '  Dep:')
        self.StoreList(aUnit,self.fInstallCommandList,'  Cmd:')
        return
    def StoreList(self,aUnit,aList,aTag):
        aUnit.write('  Num:%i\n' % (len(aList)))
        for __Item in aList:
            aUnit.write(aTag+repr(__Item)+LF)
        return
    def Report(self,aUnit):
        self.ReportLine(aUnit,self.fName,              TAG_PACKAGE)
        self.ReportLine(aUnit,self.fVersion,           TAG_VERSION)
        self.ReportBlankLine(aUnit)
        self.ReportList(aUnit,self.fArchiveList,       TAG_ARCHIVE)
        self.ReportList(aUnit,self.fPatchList,         TAG_PATCHES)
        self.ReportList(aUnit,self.fDependsOnList,     TAG_DEPENDS)
        self.ReportList(aUnit,self.fInstallCommandList,TAG_COMMAND)
        self.ReportBlankLine(aUnit)
        self.ReportBlankLine(aUnit)
        return
    def ReportList(self,aUnit,aList,aTag):
        for __Item in aList[:1]:
            self.ReportLine(aUnit,__Item,aTag)
            self.ReportBlankLine(aUnit)
        for __Item in aList[1:]:
            self.ReportLine(aUnit,__Item,B_MARGIN)
            self.ReportBlankLine(aUnit)
        return
    def ReportLine(self,aUnit,aLine,aTag):
        __Lines=aLine.splitlines()
        for __Line in __Lines[:1]:
            aUnit.write(aTag+__Line+LF)
        for __Line in __Lines[1:]:
            aUnit.write(B_MARGIN+__Line+LF)
        return
    def ReportBlankLine(self,aUnit):
        aUnit.write(LF)
        return
    def Load(self,aUnit):
        self.fName=aUnit.readline()[6:-1]
        self.fVersion=aUnit.readline()[6:-1]
        self.fArchiveList=self.LoadList(aUnit)
        self.fPatchList=self.LoadList(aUnit)
        self.fDependsOnList=self.LoadList(aUnit)
        self.fInstallCommandList=self.LoadList(aUnit)
        return
    def LoadList(self,aUnit):
        __Result=[]
        __Count=int(aUnit.readline()[6:-1])
        while __Count>ZERO:
            __Result.append(eval(aUnit.readline()[6:-1]))
            __Count=__Count-1
        return __Result

class cPackageList(object):
    def __init__(self):
        self.fDictionary={}
        return
    def Get(self,aKey):
        return self.fDictionary.get(aKey,None)
    def Append(self,aPackage):
        self.fDictionary[aPackage.GetKey()]=aPackage
        return
    def GetIndex(self,aSeq='key'):
        if aSeq in ['key']:
            __Result=self.fDictionary.keys()
            __Result.sort()
        elif aSeq in ['alpha']:
            __ByTitle=[(__Pkg.GetTitle().lower(),__Pkg.GetKey())  \
                      for __Pkg in self.fDictionary.values()]
            __ByTitle.sort()
            __Result=[__Key for (__Title,__Key) in __ByTitle]
        return __Result

PackageList=cPackageList()

class cFile(object):
    def close(self):
        if self.fIsAlreadyOpen:
            pass
        else:
            self.fUnit.close()
        return

class cInputFile(cFile):
    def __init__(self,aUnit=None):
        if aUnit==None:
            self.fUnit=sys.stdin
            self.fIsAlreadyOpen=True
        elif isinstance(aUnit,file):
            self.fUnit=aUnit
            self.fIsAlreadyOpen=True
        elif isinstance(aUnit,cFile):
            self.fUnit=aUnit.fUnit
            self.fIsAlreadyOpen=True
        else:
            self.fUnit=open(aUnit,'rb')
            self.fIsAlreadyOpen=False
        return
    def readline(self):
        return self.fUnit.readline()
    def readlines(self):
        return self.fUnit.readlines()

class cOutputFile(cFile):
    def __init__(self,aUnit=None):
        if aUnit==None:
            self.fUnit=sys.stdout
            self.fIsAlreadyOpen=True
        elif isinstance(aUnit,file):
            self.fUnit=aUnit
            self.fIsAlreadyOpen=True
        elif isinstance(aUnit,cFile):
            self.fUnit=aUnit.fUnit
            self.fIsAlreadyOpen=True
        else:
            self.fUnit=open(aUnit,'wb')
            self.fIsAlreadyOpen=False
        return
    def write(self,aBuffer):
        self.fUnit.write(aBuffer)
        return

def Store(aUnit=None,aSeq='key'):
    __Unit=cOutputFile(aUnit)
    __Index=PackageList.GetIndex(aSeq)
    __Unit.write(str(len(__Index))+LF)
    for __Key in __Index:
        PackageList.Get(__Key).Store(__Unit)
    sys.stderr.write('%i packages.\n' % len(__Index))
    __Unit.close()
    return

def Report(aUnit=None,aSeq='key'):
    __Unit=cOutputFile(aUnit)
    __Index=PackageList.GetIndex(aSeq)
    for __Key in __Index:
        PackageList.Get(__Key).Report(__Unit)
    sys.stderr.write('%i packages.\n' % len(__Index))
    __Unit.close()
    return

def ReportList(aList,aUnit=None):
    __Unit=cOutputFile(aUnit)
    for __Key in aList:
        __Package=PackageList.Get(__Key)
        if __Package==None:
            pass
        else:
            __Unit.write(__Package.GetNameVersion()+LF)
    __Unit.close()
    return

def Load(aUnit=None):
    __Unit=cInputFile(aUnit)
    __Count=int(__Unit.readline()[:-1])
    while __Count>ZERO:
        __NewPackage=cPackage()
        __NewPackage.Load(__Unit)
        PackageList.Append(__NewPackage)
        __Count=__Count-1
    __Unit.close()
    return

def GetWishList(aUnit=None):
    __WishList=cInputFile(aUnit)
    __List=__WishList.readlines()
    __WishList.close()
    __Ndx=ZERO
    while __Ndx<len(__List):
        __Line=__List[__Ndx]
        __Pos=__Line.find('#')
        if __Pos==NA:
            pass
        else:
            __Line=__Line[:__Pos]
            __List[__Ndx]=__Line
        __Pos=__Line.find('(')
        if __Pos==NA:
            pass
        else:
            __Line=__Line[:__Pos]
            __List[__Ndx]=__Line
        __Ndx=__Ndx+1
    __Result=SP.join(__List).split()
    return __Result

# Fin
