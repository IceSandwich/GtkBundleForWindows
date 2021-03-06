# -*- coding: utf-8 -*-
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import os, json, shutil
from distutils import dir_util

VCPKG_ROOT = R"E:\Programs\vcpkg"                                  # vcpkg安装目录
VCPKG_TRIPLET = "x64-windows"                                      # 架构
GTK_PKG = "gtkmm"                                                  # 提取的包名称
GTK_BUNDLE = R"E:\Program\gtkbundle"                               # 旧版bundle，用于提取pkg-config
OUTPUT_DIR = R"F:\gtk3-bundle_{}".format(VCPKG_TRIPLET)            # 输出文件夹

LogFile = None

def ReadPkg(pkgName) -> dict:
    """ 读取包信息 """
    vcpkgFile = os.path.join(VCPKG_ROOT, "ports", pkgName, "vcpkg.json")

    if os.path.exists(vcpkgFile): # 新旧版本的vcpkg，包管理不一样
        f = open(vcpkgFile, 'r')
        vcpkgJson = json.load(f)
        vcpkgJson['isNewVcpkg'] = True
        f.close()
        return vcpkgJson
    else:
        f = open(os.path.join(VCPKG_ROOT, "ports", pkgName, "CONTROL"), 'r')
        vcpkgJson = { x.split(':')[0].strip(): x.split(':')[1].strip() for x in f.readlines() if x.strip() != '' }
        def delTag(x:str)->str: # 去掉后面的括号，比如 cairo[gobject] -> cairo 或者 libuuid (!windows&!osx) -> libuuid
            def deltag(x:str, tag:str)->str:
                startpoint = x.find(tag)
                if startpoint == -1:
                    return x.strip()
                return x[:startpoint].strip()
            return deltag(deltag(x, '['), '(')
        if 'Build-Depends' in vcpkgJson:
            vcpkgJson['dependencies'] = [ delTag(x) for x in vcpkgJson['Build-Depends'].split(',') ]
        vcpkgJson['isNewVcpkg'] = False
        f.close()
        return vcpkgJson

def PrintPkgInfo(pkgName) -> str:
    """ 返回并打印包名称 """
    vcpkgJson = ReadPkg(pkgName)
    if vcpkgJson["isNewVcpkg"]:
        print("- package {}, version {}, with new vcpkg.".format(vcpkgJson["name"], vcpkgJson["version"]))
        return vcpkgJson["name"]
    else:
        print("- package {}, version {}".format(vcpkgJson["Source"], vcpkgJson["Version"]))
        return vcpkgJson["Source"]

def ReadDepends(pkgName:str, depends:set) -> bool:
    """ 读取依赖，依赖输出到depends中，若有新的依赖输出则返回true """
    vcpkgJson = ReadPkg(pkgName)

    if "dependencies" not in vcpkgJson: # no dependency package
        return False
    ret = False
    for dependency in vcpkgJson["dependencies"]:
        if isinstance(dependency, dict):
            dependency = dependency["name"]
        assert(isinstance(dependency, str))
        if 'vcpkg' in dependency: # skip vcpkg package
            continue
        depends.add(dependency)
        ret = ret or ReadDepends(dependency, depends)
    if "default-features" in vcpkgJson:
        for dependency in vcpkgJson["default-features"]:
            assert('vcpkg' not in dependency)
            depends.add(dependency)
    return ret

def BuildStructure():
    """ 建立目录结构 """
    for folderName in ["bin", "etc", "include", "lib", "share", "src", "debug"]:
        sourceDir = os.path.join(OUTPUT_DIR, folderName)
        if not os.path.exists(sourceDir):
            os.mkdir(sourceDir)
            LogFile.write("{}\n".format(folderName))

def CopySingleFile(source:str, target:str):
    """ 复制单个文件同时记录log，注意: target不要带OUTPUT_DIR """
    shutil.copy(source, os.path.join(OUTPUT_DIR, target))
    LogFile.write("{} -> {}\n".format(source, target))

def CopyTree(sourceDir:str, targetDir:str, WithHead:bool = False):
    """ 复制单个目录同时记录log，注意: 当WithHead=False时，sourceDir不要带VCPKG_ROOT，targetDir永远不要带OUTPUT_DIR """
    if WithHead:
        dir_util.copy_tree(sourceDir, os.path.join(OUTPUT_DIR, targetDir))
    else:
        dir_util.copy_tree(os.path.join(VCPKG_ROOT, sourceDir), os.path.join(OUTPUT_DIR, targetDir))
    LogFile.write("{} -> {}\n".format(sourceDir, targetDir))

def CopyPkg(pkgName):
    """ 复制包 """
    dirPath = os.path.join("packages", "{}_{}".format(pkgName, VCPKG_TRIPLET))
    dirFullPath = os.path.join(VCPKG_ROOT, dirPath)
    if not os.path.exists(dirFullPath): # has nothing to copy
        return

    dirs = os.listdir(dirFullPath)
    for folderName in ["bin", "etc", "include", "lib", "share", "debug"]:
        if folderName not in dirs: # skip if it doesn't exists
            continue
        CopyTree(os.path.join(dirPath, folderName), folderName)

    if 'tools' in dirs:
        CopyTree(os.path.join(dirPath, "tools", pkgName), "bin")

    if 'gdk-pixbuf-2.0' in dirs: # for gdk-pixbuf package
        CopyTree(os.path.join(dirPath, "gdk-pixbuf-2.0"), "lib")

def ReName(sourceDir:str, targetDir:str):
    os.rename(os.path.join(OUTPUT_DIR, sourceDir), os.path.join(OUTPUT_DIR, targetDir))
    LogFile.write("{} --> {}\n".format(sourceDir, targetDir))

def CopyPc():
    """ 仅当 gtk3 时使用 """
    CopyTree(os.path.join(GTK_BUNDLE, "lib", "pkgconfig"), os.path.join("lib", "pkgconfig"))
    for pkgName, pkgVer in [ ['gtk', '3.0'], ['pango', '1.0'], ['atk', '1.0'], ['pixman', '1'], ['glib', '2.0'], ['gtkmm', '3.0']]:
        ReName(os.path.join("include", pkgName), os.path.join("include", "{}-{}".format(pkgName, pkgVer)))
    ReName(os.path.join("include", "libpng15"), os.path.join("include", "libpng16"))

    import gtkmakepkg
    gtkmakepkg.OUTPUT_DIR = OUTPUT_DIR
    gtkmakepkg.VCPKG_ROOT = VCPKG_ROOT
    gtkmakepkg.VCPKG_TRIPLET = VCPKG_TRIPLET
    MakePkgConfig = gtkmakepkg.MakePkgConfig

    MakePkgConfig("cairomm", pkgName2="data", pcPkgName="cairomm")
    MakePkgConfig("pangomm", pkgName2="pango", pcPkgName="pangomm")
    MakePkgConfig("atkmm", pkgName2="atk", pcPkgName="atkmm")
    MakePkgConfig("gtkmm", pkgName2="gtk", pcPkgName='gtkmm')
    MakePkgConfig("gtkmm", pkgName2="gdk", pcPkgName='gdkmm')

def main():
    # 读取包信息及其依赖
    dependencies = set()
    dependencies.add(PrintPkgInfo(GTK_PKG))
    ReadDepends(GTK_PKG, dependencies)

    # 建立目录
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 复制依赖
    global LogFile
    LogFile = open(os.path.join(OUTPUT_DIR, "log.txt"), 'w')
    BuildStructure()
    for dependency in dependencies:
        print("- found depend {}".format(dependency))
        CopyPkg(dependency)

    CopyPkg("libjpeg-turbo") # required by gdk-pixbuf-2.0
    CopyPkg("liblzma") # required by libtiff-4

    CopySingleFile(os.path.join(GTK_BUNDLE, "bin", "pkg-config.exe"), os.path.join("bin", "pkg-config.exe"))
    CopyTree(os.path.join("installed", VCPKG_TRIPLET, "etc"), "etc")

    LogFile.close()

if __name__ == "__main__":
    main()