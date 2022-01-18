
LogFile = None
LogFileFileName = R'E:\Programs\vcpkg\buildtrees\gtkmm\build-x64-windows-rel-out.log'

def ExtractFileFromLine(line:str) -> str:
    """ 从行中提取文件位置 """
    endpoint = line.index(': error C4819')
    startpoint = line.find('>')
    line = line[startpoint+1:endpoint].strip()
    endpoint = line.find('(')
    if endpoint != -1:
        line = line[:endpoint]
    return line

def ChangeEncoding(filename:str, encoding:str, fromencoding:str='utf-8'):
    """ 修改编码 """
    f = open(filename, 'r', encoding=fromencoding)
    data = f.read()
    f.close()

    f = open(filename, 'wb')
    f.write(data.encode(encoding))
    f.close()

def main():
    # test
    # ExtractFileFromLine(R"     3>e:\programs\vcpkg\installed\x64-windows\include\gtk\gtkmenu.h : error C4819: The file contains a character that cannot be represented in the current code page (936). S")
    # ExtractFileFromLine(R"  3>e:\programs\vcpkg\installed\x64-windows\include\gtk\gtkenums.h(925): error C4819: The file contains a character that cannot")
    # ChangeEncoding(R"e:\programs\vcpkg\installed\x64-windows\include\gdk\gdktypes.h", "mbcs")

    LogFile = open(LogFileFileName, 'r', encoding='utf-8')

    files = list(set([ ExtractFileFromLine(x) for x in LogFile.readlines() if 'error C4819' in x ]))
    for filename in files:
        print("detect", filename)
        ChangeEncoding(filename, "mbcs")

    LogFile.close()

if __name__ == '__main__':
    main()
