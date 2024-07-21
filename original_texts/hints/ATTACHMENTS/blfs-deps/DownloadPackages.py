#!/usr/bin/python

# DownloadPackages.py
# 2004 MAR 05 . ccr

# Prepare wget script for the package names in wishlist.

# 2004 APR 18 . ccr . Regularize command-line options.
# 2004 APR 29 . ccr . Write patch names, not archive names (per Zoltan).

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

# Mainline begins here.

__Parser=optparse.OptionParser()
__DefaultPkgsDB=os.path.join(os.getcwd(),'pkgs.dat')
__Parser.add_option('-P','--PackageDB',
                    help='Package database.  Default is %s.' % (__DefaultPkgsDB),
                    default=__DefaultPkgsDB)
__Parser.add_option('-O','--OutputRept',
                    help='Output file name to receive report.  Default is > stdout.')
__Parser.add_option('-W','--WishList',
                    help="File containing a list of prospective packages.  Default is < stdin.")
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

__CountArchives=__CountPatches=ZERO
PackageDB.Load(OPTS.PackageDB)
__WishList=PackageDB.GetWishList(OPTS.WishList)
__Unit=PackageDB.cOutputFile(OPTS.OutputRept)
for __Key in __WishList:
    __Package=PackageDB.PackageList.Get(__Key)
    if __Package==None:
        pass
    else:
        for __Archive in __Package.fArchiveList:
            __Unit.write("wget %s\n" % (__Archive))
            __CountArchives=__CountArchives+1
        for __Patch in __Package.fPatchList:
            __Unit.write("wget %s\n" % (__Patch)) # 2004 APR 29
            __CountPatches=__CountPatches+1
sys.stderr.write("%i archives.  %i patches.\n" % (__CountArchives,__CountPatches))
__Unit.close()
# Fin
