#!/usr/bin/python

# MaskDonePackages.py
# 2004 MAR 05 . ccr

# Eliminate packages from the wishlist that are already installed.

# 2004 APR 18 . ccr . Regularize command-line options.

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
__DefaultDoneList=os.path.join(os.getcwd(),'donelist.txt')
__Parser.add_option('-O','--OutputRept',
    help='Output file name to receive report.  Default is > stdout.')
__Parser.add_option('-W','--WishList',
    help='File containing a list of prospective packages.  Default is < stdin.')
__Parser.add_option('-D','--DoneList',
    help='File containing a list of packages already installed.  Default is %s.' % (__DefaultDoneList),
    default=__DefaultDoneList)
(OPTS,__Args)=__Parser.parse_args()
if len(__Args)>ZERO:
    __Parser.error('Arguments are prohibited.')
if os.path.exists(OPTS.DoneList):
    pass
else:
    __Parser.error(OPTS.DoneList+' not found.')
if OPTS.OutputRept in [None,NULL,'> stdout']:
    OPTS.OutputRept=None
if OPTS.WishList in [None,NULL,'< stdin']:
    OPTS.WishList=None
else:
    if os.path.exists(OPTS.WishList):
        pass
    else:
        __Parser.error(OPTS.WishList+' not found.')

__WishList=PackageDB.GetWishList(OPTS.WishList)
__DoneList=PackageDB.GetWishList(OPTS.DoneList)
__Unit=PackageDB.cOutputFile(OPTS.OutputRept)
__Result=[]
for __Key in __WishList:
    if (__Key in __DoneList) or (__Key in __Result):
        pass
    else:
        __Result.append(__Key)
__Unit.write(LF.join(__Result)+LF)
sys.stderr.write('%i wanted.  %i done.  %i to do.\n' % \
                 (len(__WishList),len(__DoneList),len(__Result)))
__Unit.close()
# Fin
