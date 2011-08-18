#!/usr/bin/env python3
# Created By: Virgil Dupras
# Created On: 2011-06-20
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "GPL v3" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/gplv3_license

import sys
import os
import os.path as op
import compileall
import shutil
import json

from hscommon.build import (build_dmg, copy_packages, build_debian_changelog, copy_qt_plugins,
    print_and_do, get_module_version)

def package_windows(dev):
    from cx_Freeze import Freezer, Executable
    app_version = get_module_version('core')
    if op.exists('dist'):
        shutil.rmtree('dist')
    
    exe = Executable(
        targetName = 'PdfMasher.exe',
        script = 'run.py',
        base = 'Win32GUI',
        icon = 'images\\main_icon.ico',
    )
    freezer = Freezer(
        [exe],
        # Since v4.2.3, cx_freeze started to falsely include tkinter in the package. We exclude it explicitly because of that.
        excludes = ['tkinter'],
    )
    freezer.Freeze()
    
    # Now we have to copy pdfminder's cmap to our root dist dir (We'll set CMAP_PATH env at runtime)
    import pdfminer.cmap
    cmap_src = op.dirname(pdfminer.cmap.__file__)
    cmap_dest = op.join('dist', 'cmap')
    shutil.copytree(cmap_src, cmap_dest)
    
    if not dev:
        # Copy qt plugins
        plugin_dest = op.join('dist', 'qt4_plugins')
        plugin_names = ['accessible', 'codecs', 'iconengines', 'imageformats']
        copy_qt_plugins(plugin_names, plugin_dest)
        
        # Compress with UPX 
        libs = [name for name in os.listdir('dist') if op.splitext(name)[1] in ('.pyd', '.dll', '.exe')]
        for lib in libs:
            print_and_do("upx --best \"dist\\{0}\"".format(lib))
    
    help_path = 'build\\help'
    print("Copying {0} to dist\\help".format(help_path))
    shutil.copytree(help_path, 'dist\\help')
    
    if not dev:
        # AdvancedInstaller.com has to be in your PATH
        # this is so we don'a have to re-commit installer.aip at every version change
        shutil.copy('qt\\installer.aip', 'installer_tmp.aip')
        print_and_do('AdvancedInstaller.com /edit installer_tmp.aip /SetVersion {}'.format(app_version))
        print_and_do('AdvancedInstaller.com /build installer_tmp.aip -force')
        os.remove('installer_tmp.aip')
    

def package_debian():
    app_version = get_module_version('core')
    destpath = op.join('build', 'pdfmasher-{}'.format(app_version))
    if op.exists(destpath):
        shutil.rmtree(destpath)
    srcpath = op.join(destpath, 'src')
    os.makedirs(srcpath)
    shutil.copy('run.py', op.join(srcpath, 'run.py'))
    copy_packages(['qt', 'ebooks', 'hscommon', 'core', 'qtlib', 'pdfminer', 'ply', 'jobprogress', 'markdown', 'cssutils'], srcpath)
    import sip, PyQt4
    shutil.copy(sip.__file__, srcpath)
    qtsrcpath = op.dirname(PyQt4.__file__)
    qtdestpath = op.join(srcpath, 'PyQt4')
    os.makedirs(qtdestpath)
    shutil.copy(op.join(qtsrcpath, '__init__.py'), qtdestpath)
    shutil.copy(op.join(qtsrcpath, 'Qt.so'), qtdestpath)
    shutil.copy(op.join(qtsrcpath, 'QtCore.so'), qtdestpath)
    shutil.copy(op.join(qtsrcpath, 'QtGui.so'), qtdestpath)
    shutil.copytree('debian', op.join(destpath, 'debian'))
    build_debian_changelog(op.join('help', 'changelog'), op.join(destpath, 'debian', 'changelog'),
        'pdfmasher', from_version='0.1.0')
    shutil.copytree(op.join('build', 'help'), op.join(srcpath, 'help'))
    shutil.copy(op.join('images', 'logo_small.png'), srcpath)
    compileall.compile_dir(srcpath)
    os.chdir(destpath)
    os.system("dpkg-buildpackage")

def main():
    conf = json.load(open('conf.json'))
    ui = conf['ui']
    dev = conf['dev']
    print("Packaging PdfMasher with UI {0}".format(ui))
    if ui == 'cocoa':
        build_dmg('cocoa/build/release/PdfMasher.app', '.')
    elif ui == 'qt':
        if sys.platform == "win32":
            package_windows(dev)
        elif sys.platform == "linux2":
            package_debian()
        else:
            print("Qt packaging only works under Windows or Linux.")

if __name__ == '__main__':
    main()
