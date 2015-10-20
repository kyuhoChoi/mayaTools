# -*- coding:utf-8 -*-
import os
import stat
import locale
import time

locale.setlocale(locale.LC_ALL, '')

'''
import dirWork
dirWork.getDirData('D:/Users/Desktop')
'''

def getDirData(_path, _sort, _reverse, _print):
    _path=_path.replace('\\','/')    

    _result = []
    _listDir = os.listdir(_path)

    for _item in _listDir:
        _filePath = _path+'/'+_item
        _file = os.path.basename(_item)
        _ext = os.path.splitext(_item)[1][1:]
        _type = ''

        # 종류표시
        if   os.path.isfile(_filePath):
            _type = 'file'
        elif os.path.isdir(_filePath):
            _type = 'dir'
        elif os.path.islink(_filePath):
            _type = 'link'
        elif os.path.ismount(_filePath):
            _type = 'mount'

        # 크기     
        _size = os.stat(_filePath)[stat.ST_SIZE]
        _subfix = 'byte'
        _fsize = 1.0
        
        if _size>1024:
            _fsize = _size/1024.0
            _subfix = 'Kb  '

        if _size>1048576:
            _fsize = _size/1048576.0
            _subfix = 'Mb  '

        if _size>1.0737e+9:
            _fsize = _size/1.0737e+9
            _subfix = 'Gb  '

        _fileSize = locale.format('%.1f ', _fsize, True) + _subfix

        # 생성시간        
        _ctime = time.localtime(os.path.getctime(_filePath))
        _ctime = '%04d %02d.%02d %02d:%02d'%(_ctime[0],_ctime[1],_ctime[2],_ctime[3],_ctime[4])

        # 최근 수정시간
        _mtime = time.localtime(os.path.getmtime(_filePath))
        _mtime = '%04d %02d.%02d %02d:%02d'%(_mtime[0],_mtime[1],_mtime[2],_mtime[3],_mtime[4])

        # 결과 저장
        _result.append( {'type':_type, 'ext':_ext, 'size':_size, 'fsize':_fileSize, 'ctime':_ctime, 'mtime':_mtime, 'name':_file } )
    
    # 사전형 정렬
    if _sort:
        for _key in _sort:
            _result = [_val for (_key,_val) in sorted([(_dicItem[ _key ],_dicItem) for _dicItem in _result])]
            if _reverse:
                _result.reverse()

    # 내용 출력
    if _print:
        print "Directory =", _path
        for _item in _result:
            _mtime = _item['mtime']
            if _item['ctime'] == _mtime:
                _mtime = ''

            print _item['name'].ljust(30)[:30], _item['type'].rjust(5), _item['ext'].ljust(5), _item['fsize'].rjust(12), _item['ctime'].center(20), _mtime.center(20)

    return _result

getDirData('D:/Users/Desktop',['ext'], False, True)