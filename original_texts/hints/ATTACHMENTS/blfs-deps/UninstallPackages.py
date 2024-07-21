#!/usr/bin/python

# UninstallPackages.py
# 2004 MAR 18 . ccr

# Attempt 'make uninstall' on  package names in wishlist.

# 2004 APR 18 . ccr . Regularize command-line options.

import sys
import os
import urlparse
import optparse
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

UNARCH_TYPES={'tar.gz':('tar -z','x','t','f'),
              'tgz':('tar -z','x','t','f'),
              'tar.bz2':('tar -j','x','t','f'),
              'zip':(NULL,'mkdir unArch && unzip -d unArch','zipinfo -1',NULL)}

class cSrc(object):
    def __init__(self,aFile=None,aURL=None):

        def ExtractSrc(aURL):
            (__NetScheme,__Domain,__Path,__Opts,__Anchor)= \
                urlparse.urlsplit(aURL)
            (__DirPath,__Base)=os.path.split(__Path)
            if __Base==aURL:
                aURL=None
            return (__Base,aURL)
        
        self.fFile=aFile
        self.fURL=aURL
        if (self.fFile==None) and (self.fURL==None):
            pass
        elif (self.fFile==None):
            (self.fFile,self.fURL)=ExtractSrc(self.fURL)
        elif (self.fURL==None):
            (self.fFile,self.fURL)=ExtractSrc(self.fFile)
        return

def GetArchType(aArchive):
    __X=aArchive.lower().split('.')
    __Type=None
    if len(__X)>1:
        if __X[-2] in 'tar':
            __Type='%s.%s' % tuple(__X[-2:])
        else:
            __Type=__X[-1]
    return __Type

def GetUnArchCommand(aFunction,aArchive):
    __Type=GetArchType(aArchive)
    __S=UNARCH_TYPES.get(__Type,None)
    if __S==None:
        return None
    else:
        (__Prolog,__ExtractOpt,__ListOpt,__Epilog)=__S
        if aFunction.lower() in ['list']:
            __Opt=__ListOpt
        elif aFunction.lower() in ['extract']:
            __Opt=__ExtractOpt
        else:
            return None
    return '%s%s%s %s' % (__Prolog,__Opt,__Epilog,aArchive)

def DiagnoseMissingArchive(aArchive):
    UNIT.write('echo %s not found.\nexit 2\n' % (aArchive))
    return

def GetSrcDirList(aArchiveList):
    global OPTS
    __SrcDirs=[]
    for __Src in aArchiveList:
        __Arch=cSrc(aURL=__Src).fFile
        __ArchPath=os.path.join(OPTS.SourcePath,__Arch)
        if os.path.exists(__ArchPath):
            if GetArchType(__Arch) in ['zip']:
                return ['unArch']
            __Cmd=GetUnArchCommand('list',__ArchPath)
            if __Cmd==None:
                pass
            else:
                if OPTS.Verbose==True:
                    sys.stderr.write('Listing %s\n' % (__Arch))
                __Pipe=os.popen(__Cmd,'r')
                __SrcDirs.extend(__Pipe.read().split())
                __Pipe.close()
        else:
            DiagnoseMissingArchive(__Arch)
    __Result={} # Dictionary of unique values.
    for __Dir in __SrcDirs:
        __S=__Dir.split('/')
        if len(__S)>1:
            __Result[__S[ZERO]]=None
    return __Result.keys()

def Truncate(aLine):
    __Pos=aLine.find('make')
    if __Pos==NA:
        return NULL
    else:
        return aLine[:__Pos]+'make uninstall'

# Mainline begins here.

__Parser=optparse.OptionParser()
__DefaultPkgsDB=os.path.join(os.getcwd(),'pkgs.dat')
__Parser.add_option('-P','--PackageDB',
                    help='Package database.  Default is %s.' % (__DefaultPkgsDB),
                    default=__DefaultPkgsDB)
__Parser.add_option('-W','--WishList',
                    help='File containing a list of prospective packages.  Default is < stdin.')
__Parser.add_option('-O','--OutputRept',
                    help='Output file name to receive report.  Default is > stdout.')
__Parser.add_option('-S','--SourcePath',
                    help='Source library.  Default is /usr/src.',
                    default='/usr/src')
__Parser.add_option('-V','--Verbose',
                    action='store_true',
                    help='List package names during processing.',
                    default=False)
(OPTS,__Args)=__Parser.parse_args()
if len(__Args)>ZERO:
    __Parser.error('Arguments are prohibited.')
if os.path.exists(OPTS.PackageDB):
    pass
else:
    __Parser.error(OPTS.PackageDB+' not found.')
if OPTS.OutputRept in [None,NULL,'> stdout']:
    OPTS.OutputRept=None
if OPTS.WishList in [None,NULL,'< stdin']:
    OPTS.WishList=None
else:
    if os.path.exists(OPTS.WishList):
        pass
    else:
        __Parser.error(OPTS.WishList+' not found.')

PackageDB.Load(OPTS.PackageDB)
__WishList=PackageDB.GetWishList(OPTS.WishList)
UNIT=PackageDB.cOutputFile(OPTS.OutputRept)
UNIT.write('''#!/bin/bash
# Uninstall Code Fragments from BEYOND LINUX FROM SCRATCH
# >>>====> to be run from the path that contains the archives <====<<<
''')
UNIT.write('SrcArchive=%s\n' % (OPTS.SourcePath))
__Count=ZERO
__WishList.reverse()
for __Key in __WishList:
    UNIT.write('function Uninstall_%s {\n' % (__Key))
    __Package=PackageDB.PackageList.Get(__Key)
    if __Package==None:
        pass
    else:
        __UnMake=NULL
        for __Code in __Package.fInstallCommandList[:1]:
            __UnMake=Truncate(__Code)
        if __UnMake==NULL:
            pass
        else:
            __SrcDirList=GetSrcDirList(__Package.fArchiveList)
            for __Archive in __Package.fArchiveList:
                __Arch=cSrc(aURL=__Archive).fFile
                __Cmd=GetUnArchCommand('extract',__Arch)
                UNIT.write('%s &&\n' % (__Cmd))
            if len(__SrcDirList)>ZERO:
                UNIT.write('cd %s &&\n' % (__SrcDirList[ZERO]))
            UNIT.write('(\n%s\n)\n' % (__UnMake))
            UNIT.write('cd $SrcArchive\n')
            if len(__SrcDirList)>ZERO:
                for __Dir in __SrcDirList:
                    UNIT.write('rm -rf %s\n' % (__Dir))
            __Count=__Count+1
        __Log=os.path.join('/var/log/install-log',__Key)
        if os.path.exists(__Log):
            __Files=PackageDB.GetWishList(__Log)
            for __Fn in __Files:
                UNIT.write('rm -f %s\n' % (__Fn))
            UNIT.write('mv %s %s.del\n' % (__Log,__Log))
    UNIT.write('}\n')
for __Key in __WishList:
    UNIT.write('Uninstall_%s\n' % (__Key))
UNIT.write('echo fin!\n')
sys.stderr.write('%i packages.\n' % (__Count))
UNIT.close()
                
# Fin
