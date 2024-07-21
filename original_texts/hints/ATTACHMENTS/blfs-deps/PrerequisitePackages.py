#!/usr/bin/python

# PrerequisitePackages.py
# 2004 MAR 05 . ccr

# List packages prerequisite to the package names in wishlist.

# 2004 APR 18 . ccr . Regularize command-line options.
# 2004 APR 29 . ccr . Avoid tracing dependencies of packages already encountered (per Zoltan).

import sys
import os
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

ALTERNATES={
    'courier':['db','gdbm'],
    'gnome-libs':['db','db-3.3'],
    'gsview':['gs','espgs'],
    'mc':['GLib2','GLib'],
    'mpg123':['alsa'],
    'pciutils':['wget','lynx'],
    'qpopper':['sendmail','postfix','qmail'],
    'xine-lib':['alsa','esound','kde-core-arts']
    }

def KillAlternates(aAlternates,aDependents):
    __Alternates=[__Alt for __Alt in aAlternates]
    __Alternates.append('or')
    __Dependents=[__Dep for __Dep in aDependents \
                  if __Dep not in __Alternates]
    return __Dependents

def WalkDeps(aPackage):
    __Key=aPackage.GetKey()
    __Alternates=ALTERNATES.get(__Key,[])
    __Siblings=KillAlternates(__Alternates,
                            aPackage.GetDependencies())
    __Chosen=False
    for __Key in __Alternates:
        if __Key in DEPS:
            __Chosen=True
    if not __Chosen:
        __Siblings.extend(__Alternates[:1])
    for __Key in __Siblings:
        if __Key in DEPS:
            pass
        else:
            __Package=PackageDB.PackageList.Get(__Key)
            if __Package==None:
                pass
            else:
                WalkDeps(__Package)
    DEPS.append(aPackage.GetKey())
    return 

def GetRequirements(aPackages):
    global DEPS
    DEPS=[]
    for __Key in aPackages:
        if __Key in DEPS: # 2004 APR 29
            pass
        else:
            __Package=PackageDB.PackageList.Get(__Key)
            if __Package==None:
                pass
            else:
                WalkDeps(__Package)
    return DEPS

# Mainline begins here.

__Parser=optparse.OptionParser()
__DefaultPkgsDB=os.path.join(os.getcwd(),'pkgs.dat')
__Parser.add_option('-P','--PackageDB',
                    help='Package database.  Default is %s.' % (__DefaultPkgsDB),
                    default=__DefaultPkgsDB)
__Parser.add_option('-O','--OutputRept',
    help='Output file name to receive report.  Default is > stdout.')
__Parser.add_option('-W','--WishList',
    help="File containing a list of the target packages you're shooting for.  Default is < stdin.")
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
__Unit=PackageDB.cOutputFile(OPTS.OutputRept)
__Unit.write('# Install packages in this order:\n')
__Deps=GetRequirements(__WishList)
PackageDB.ReportList(__Deps,__Unit)
sys.stderr.write('%i packages needed.\n' % (len(__Deps)))
__Unit.close()
# Fin
