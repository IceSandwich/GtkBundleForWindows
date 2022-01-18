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
OUTPUT_DIR = R"F:\gtk4-bundle_{}".format(VCPKG_TRIPLET)            # 输出文件夹

LogFile = None

def PrintPkgInfo(pkgName) -> str:
    """ 返回包名称 """
    f = open(os.path.join(VCPKG_ROOT, "ports", pkgName, "vcpkg.json"), 'r')
    vcpkgJson = json.load(f)
    f.close()
    print("- package {}, version {}".format(vcpkgJson["name"], vcpkgJson["version"]))
    return vcpkgJson["name"]

def ReadDepends(pkgName:str, depends:set) -> bool:
    """ 读取依赖，依赖输出到depends中，若有新的依赖输出则返回true """
    f = open(os.path.join(VCPKG_ROOT, "ports", pkgName, "vcpkg.json"), 'r')
    vcpkgJson = json.load(f)
    f.close()
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

def CopyTree(sourceDir:str, targetDir:str):
    """ 复制单个目录同时记录log，注意: sourceDir和targetDir不要带VCPKG_ROOT和OUTPUT_DIR """
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