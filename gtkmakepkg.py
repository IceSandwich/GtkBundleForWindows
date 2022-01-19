# -*- coding: utf-8 -*-
import os

VCPKG_ROOT = R"E:\Programs\vcpkg"                                  # vcpkg安装目录
VCPKG_TRIPLET = "x64-windows"                                      # 架构
OUTPUT_DIR = R"F:\gtk3-bundle_{}".format(VCPKG_TRIPLET)            # 输出文件夹

def MakePkgConfig(pkgName:str, pkgName2:str = '', pcPkgName:str = ''):
    f = open(os.path.join(VCPKG_ROOT, "ports", pkgName, "CONTROL"), 'r')
    vcpkgJson = { x.split(':')[0].strip(): x.split(':')[1].strip() for x in f.readlines() if x.strip() != '' }
    f.close()

    if pcPkgName == '':
        pcPkgName = vcpkgJson["Source"]

    cleanPath = os.path.join(VCPKG_ROOT, "buildtrees", pkgName, "src")
    cleanPath = os.path.join(cleanPath, os.listdir(cleanPath)[0])
    pcFilename = sorted([ x for x in os.listdir(cleanPath) if x.endswith('.pc.in') and pcPkgName in x ], key=lambda x:len(x))
    if len(pcFilename) == 0:
        cleanPath = os.path.join(cleanPath, pkgName2)
        pcFilename = sorted([ x for x in os.listdir(cleanPath) if x.endswith('.pc.in') and pcPkgName in x ], key=lambda x:len(x))
    pcName = pcFilename[0]
    pcFilename = os.path.join(cleanPath, pcName)

    f = open(pcFilename, 'r')
    pc = f.read()
    f.close()
    
    pc = pc.replace('@prefix@', '${pcfiledir}/../..')
    pc = pc.replace('@exec_prefix@', '${prefix}')
    pc = pc.replace('@libdir@', '${exec_prefix}/lib')
    pc = pc.replace('@datarootdir@', '${prefix}/share')
    pc = pc.replace('@datadir@', '${datarootdir}')
    pc = pc.replace('@includedir@', '${prefix}/include')
    pc = pc.replace('@GDK_BACKENDS@', 'win32')

    pc = pc.replace('@VERSION@', vcpkgJson["Version"])
    pc = pc.replace('@PACKAGE_VERSION@', vcpkgJson["Version"])

    # gdkmm
    pc = pc.replace('@GTKMM_MODULE_NAME@', 'gtkmm-3.0')
    pc = pc.replace('@GDKMM_MODULES@', 'gtk+-3.0 cairomm-1.16 pangomm gdk-pixbuf-2.0')
    pc = pc.replace('@GDKMM_API_VERSION@', '3.0')
    # pc = pc.replace('@GDKMM_MODULE_NAME@', 'gdkmm-3.0')

    # gtkmm
    pc = pc.replace('@GTKMM_MODULE_NAME@', 'gtkmm-3.0')
    pc = pc.replace('@GTKMM_API_VERSION@', '3.0')
    pc = pc.replace('@GTKMM_MODULES@','gtk+-3.0 cairomm-1.16 pangomm gdk-pixbuf-2.0 atkmm')
    pc = pc.replace('@GDKMM_MODULE_NAME@', 'gdkmm') # gdkmm-3.0

    # pangomm
    pc = pc.replace('@PANGOMM_MODULE_NAME@', 'pangomm-1.4')
    pc = pc.replace('@PANGOMM_MODULES@', 'glibmm-2.4 cairomm-1.16 pangocairo')
    pc = pc.replace('@PANGOMM_API_VERSION@', '1.4')
    pc = pc.replace('@PACKAGE_TARNAME@', 'pangomm')

    # atkmm
    pc = pc.replace('@ATKMM_MODULE_NAME@', 'atkmm-1.6')
    pc = pc.replace('@ATKMM_MODULES@', 'glibmm-2.4 atk')
    pc = pc.replace('@ATKMM_API_VERSION@', '1.6')

    # cairomm
    pc = pc.replace('@CAIROMM_MODULE_NAME@', 'cairomm-1.0')
    pc = pc.replace('@CAIROMM_MODULES@', 'sigc++-2.0 cairo')
    pc = pc.replace('@CAIROMM_API_VERSION@', '1.0')

    newpcFilename = os.path.join(OUTPUT_DIR, "lib", "pkgconfig", pcName.replace('.in', ''))
    f = open(newpcFilename, "w")
    f.write(pc)
    f.close()

    print("- write {}".format(newpcFilename))

if __name__ == '__main__':
    MakePkgConfig("cairomm", pkgName2="data", pcPkgName="cairomm")
    MakePkgConfig("pangomm", pkgName2="pango", pcPkgName="pangomm")
    MakePkgConfig("atkmm", pkgName2="atk", pcPkgName="atkmm")
    MakePkgConfig("gtkmm", pkgName2="gtk", pcPkgName='gtkmm')
    MakePkgConfig("gtkmm", pkgName2="gdk", pcPkgName='gdkmm')

