#!/usr/bin/python

# ReportPackages.py
# 2004 MAR 01 . ccr

# Print a report of the package database.

# 2004 APR 18 . ccr . Regularize command-line options.

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

# Mainline.

__Parser=optparse.OptionParser()
__DefaultPkgsDB=os.path.join(os.getcwd(),'pkgs.dat')
__Parser.add_option('-P','--PackageDB',
                    help='Package database.  Default is %s.' % (__DefaultPkgsDB),
                    default=__DefaultPkgsDB)
__Parser.add_option('-O','--OutputRept',
                    help='Output file name to receive report.  Default is > stdout.')
(OPTS,__Args)=__Parser.parse_args()
if len(__Args)>ZERO:
    __Parser.error('Arguments are prohibited.')
if os.path.exists(OPTS.PackageDB):
    pass
else:
    __Parser.error(OPTS.PackageDB+' not found.')
if OPTS.OutputRept in [None,NULL,'> stdout']:
    OPTS.OutputRept=None

PackageDB.Load(OPTS.PackageDB)
PackageDB.Report(OPTS.OutputRept,aSeq='alpha')
# Fin
