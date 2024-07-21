#!/usr/bin/python

# AuditPackages.py
# 2004 MAR 01 . ccr

# Fix up the package database.

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

def Shadow():
    if PackageDB.PackageList.Get('shadow')==None:
        __Shadow=PackageDB.cPackage()
        __Shadow.SetNameVersion('shadow','Shadow-4.0.3')
        __Shadow.AppendPatch('http://www.linuxfromscratch.org/patches/blfs/5.0/shadow-4.0.3-pam-2.patch')
        __Shadow.AppendDependency('Linux_PAM')
        __Shadow.AppendCommand('''patch -Np1 -i ../shadow-4.0.3-parm-2.patch &&
./configure --prefix-/usr --libdir=/usr/lib --enable-shared --with-libpam &&
make &&
make install &&
ln -sf vipw /usr/sbin/vigr &&
rm /bin/vipw &&
mv /bin/sg /usr/bin &&
mv /usr/lib/lib{misc,shadow}.so.0* /lib &&
ln -sf ../../lib/libshadow.so.0 /usr/lib/libshadow.so &&
ln -sf ../../lib/libmisc.so.0 /usr/lib/libmisc.so &&
cp debian/securetty /etc/securetty''')
        PackageDB.PackageList.Append(__Shadow)
    return

def XFree86():
    __XFree86=PackageDB.PackageList.Get('xfree86')
    if (__XFree86!=None) and \
           (__XFree86.CountArchives()==1):
        __Archive=__XFree86.fArchiveList[ZERO]
        __SubDirs=__Archive.split('/')
        if (len(__SubDirs)>=2) and \
               (__SubDirs[-2]=='source'):
            __XFree86.fArchiveList[ZERO]=__Archive+'X430src-1.tgz'
            __XFree86.fArchiveList.append(__Archive+'X430src-2.tgz')
            __XFree86.fArchiveList.append(__Archive+'X430src-3.tgz')
            __XFree86.fArchiveList.append(__Archive+'X430src-4.tgz')
            __XFree86.fArchiveList.append(__Archive+'X430src-5.tgz')
            __XFree86.fArchiveList.append(__Archive+'X430src-6.tgz')
            __XFree86.fArchiveList.append(__Archive+'X430src-7.tgz')
            __XFree86.fPatchList.append('ftp://ftp.xfree86.org/pub/XFree86/4.3.0/fixes/4.3.0-4.3.0.1.diff.gz')
    return

def KDECore():
    if PackageDB.PackageList.Get('kde-core')==None:
        __KDE=PackageDB.cPackage()
        __KDE.SetNameVersion('kde-core','KDE')
        __KDE.AppendDependency('kde-core-arts')
        __KDE.AppendDependency('kde-libs')
        __KDE.AppendDependency('kde-base')
        PackageDB.PackageList.Append(__KDE)
    return

def GnomeCore():
    if PackageDB.PackageList.Get('gnome-core')==None:
        __Gnome=PackageDB.cPackage()
        __Gnome.SetNameVersion('gnome-core','Gnome')
        __Gnome.AppendDependency('gnome-desktop')
        __Gnome.AppendDependency('gnome-panel')
        __Gnome.AppendDependency('gnome-session')
        __Gnome.AppendDependency('control-center')
        __Gnome.AppendDependency('xfree86')
        __Gnome.AppendDependency('GRK2')
        __Gnome.AppendDependency('libpng')
        __Gnome.AppendDependency('libjpeg')
        __Gnome.AppendDependency('libtiff')
        __Gnome.AppendDependency('popt')
        PackageDB.PackageList.Append(__Gnome)
    return

def Alsa():
    if PackageDB.PackageList.Get('alsa')==None:
        __Alsa=PackageDB.cPackage()
        __Alsa.SetNameVersion('alsa','ALSA-0.9.6')
        __Alsa.AppendDependency('alsa-driver')
        __Alsa.AppendDependency('alsa-lib')
        __Alsa.AppendDependency('alsa-oss')
        __Alsa.AppendDependency('alsa-tools')
        __Alsa.AppendDependency('alsa-utils')
        PackageDB.PackageList.Append(__Alsa)
    return

def Sane():
    __Sane=PackageDB.PackageList.Get('sane')
    if (__Sane!=None) and \
           (__Sane.CountArchives()==1):
        __Sane.AppendArchive('ftp://ftp.mostang.com/pub/sane/sane-backends-1.0.12/sane-backends-1.0.12.tar.gz')
    return

def Xine():
    __Xine=PackageDB.PackageList.Get('xine-lib')
    if __Xine==None:
        pass
    else:
        if 'arts' in __Xine.fDependsOnList:
            __Ndx=__Xine.fDependsOnList.index('arts')
            __Xine.fDependsOnList[__Ndx]='kde-core-arts'
    return

def LibGnome():
    __LibGnome=PackageDB.PackageList.Get('libgnome')
    if __LibGnome==None:
        pass
    else:
        if 'libbonobo' in __LibGnome.fDependsOnList:
            pass
        else:
            __LibGnome.fDependsOnList.append('libbonobo')
    return

# Mainline begins here:

__Parser=optparse.OptionParser()
__DefaultPkgsDB=os.path.join(os.getcwd(),'pkgs.dat')
__Parser.add_option('-P','--PackageDB',
                    help='Package database.  Default is %s.' % (__DefaultPkgsDB),
                    default=__DefaultPkgsDB)
__Parser.add_option('-O','--OutputRept',
                    help='Output file name to receive report.  Default is > stdout.')
__Parser.add_option('-A','--NoArchive',
                    action='store_true',
                    help='List packages that have no archives.',
                    default=False)
__Parser.add_option('-C','--NoCommand',
                    action='store_true',
                    help='List packages that have no install code fragments.',
                    default=False)
__Parser.add_option('-U','--UnsatisfiedExternals',
                    action='store_true',
                    help='List packages that depend on unknown packages.',
                    default=False)
__Parser.add_option('-S','--StandAlone',
                    action='store_true',
                    help='List packages that are not depended upon by other packages.',
                    default=False)
__Parser.add_option('-L','--ListAll',
                    action='store_true',
                    help='List all package names.',
                    default=False)
__Parser.add_option('-I','--ImpactOf',
                    metavar='PACKAGE',
                    help='List packages that immediately depend on PACKAGE.')
__Parser.add_option('-F','--Fix',
                    action='store_true',
                    help='Update the package database with patches for known omissions.',
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

PackageDB.Load(OPTS.PackageDB)
__Unit=PackageDB.cOutputFile(OPTS.OutputRept)
__Index=PackageDB.PackageList.GetIndex()

if OPTS.Fix:
    Shadow()
    XFree86()
    KDECore()
    GnomeCore()
    Alsa()
    Sane()
    Xine()
    LibGnome()
    PackageDB.Store(OPTS.PackageDB)

if OPTS.NoArchive:
    __Unit.write('# Packages that have no archives:\n')
    for __Key in __Index:
        __Package=PackageDB.PackageList.Get(__Key)
        if __Package.CountArchives()==ZERO:
            __Unit.write(__Package.GetNameVersion()+_LF)

if OPTS.NoCommand:
    __Unit.write('# Packages that have no install code fragments:\n')
    for __Key in __Index:
        __Package=PackageDB.PackageList.Get(__Key)
        if __Package.CountCommandCodeFragments()==ZERO:
            __Unit.write(__Package.GetNameVersion()+_LF)

if OPTS.UnsatisfiedExternals:
    __Unit.write('# Packages that depend on unknown packages:\n')
    for __Key in __Index:
        __Package=PackageDB.PackageList.Get(__Key)
        __Dependencies=__Package.GetDependencies()
        for __Prerequisite in __Dependencies:
            if PackageDB.PackageList.Get(__Prerequisite)==None:
                __Unit.write('%s depends on %s\n' % \
                             (__Package.GetNameVersion(),__Prerequisite))

if OPTS.StandAlone:
    __Unit.write('# Packages that are not depended upon by other packages:\n')
    __ShortList={}
    for __Key in __Index:
        __ShortList[__Key]=None
    for __Key in __Index:
        __Package=PackageDB.PackageList.Get(__Key)
        __Dependencies=__Package.GetDependencies()
        for __Prerequisite in __Dependencies:
            if (PackageDB.PackageList.Get(__Prerequisite)!=None) and \
                   __ShortList.has_key(__Prerequisite):
                del __ShortList[__Prerequisite]
    for __Key in __ShortList.keys():
        __Package=PackageDB.PackageList.Get(__Key)
        __Unit.write(__Package.GetNameVersion()+LF)

if OPTS.ListAll:
    __Unit.write('# All package names:\n')
    for __Key in __Index:
        __Package=PackageDB.PackageList.Get(__Key)
        __Unit.write(__Package.GetNameVersion()+LF)

if OPTS.ImpactOf:
    __Unit.write('# Packages that immediately depend on %s:\n' % \
                 OPTS.ImpactOf)
    for __Key in __Index:
        __Package=PackageDB.PackageList.Get(__Key)
        if OPTS.ImpactOf in __Package.GetDependencies():
            __Unit.write(__Package.GetNameVersion()+LF)

__Unit.close()
# Fin
