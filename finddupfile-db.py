# _*_ coding: utf-8 _*_
from __future__ import print_function

import glob
import hashlib
import os
import sqlite3
import sys
import time

reload(sys)
sys.setdefaultencoding("utf8")


def gethash(file_path):
    hashs = ""
    try:
        fi = open(file_path, "rb")
        line = fi.readline()
        hashs = hashlib.md5()
        while line:
            hashs.update(line)
            line = fi.readline()

        fi.close()
    except:
        pass
    return hashs.hexdigest()


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print('usage finddupfile <path name>')
        exit(1)

    conn = sqlite3.connect('allfilemd5.sqlite')
    sqlstr = 'DROP TABLE "filemd5"'

    try:
        conn.execute(sqlstr)
        conn.commit()
    except:
        print("error drop table")
    
    sqlstr = 'create table "filemd5" ("filename" varchar,"md5" varchar,"filesize" float)'
    try:
        conn.execute(sqlstr)
        conn.commit()
    except:
        print("error create table")
        exit(1)

    p = sys.argv[1]
    dirtree = os.walk(p)

    print(time.asctime(time.localtime(time.time())))
    print('_' * 80)
    
    totalsize = 0
    i = 0
    for dirname, subdir, files in dirtree:
        for s in subdir:
            if not s.startswith('.'):
                fpattern = dirname + '/' + s + '/*.*'
                f = glob.glob(fpattern)
                if len(f) >= 0:
                    for infile in f:
                        if not os.path.isdir(infile):
                            try:
                                sz = os.path.getsize(infile)
                                totalsize += sz
                                i = i + 1
                                sp = ' ' * 150
                                sys.stdout.write(sp + '\r')
                                s1 = ' process file no: ' + format(i, ',') +'\t'
                                s2 = ' size: ' + format(sz,',')
                                s2 = s2 + ' ' * (30-len(s2))
                                s3 = ' file: ' + infile[-50:] + ' ' * 10 +'\r'
                                sys.stdout.write(s1+s2+s3)
                                sys.stdout.flush()
    
                                img_md5 = gethash(infile)
                                infile = infile.replace("'", " ")
                                sqlstr = "insert into filemd5 values('{}','{}',{});" \
                                    .format(infile, img_md5, sz)
                                try:
                                    conn.execute(sqlstr)
                                    conn.commit()
                                except:
                                    print("error insert %s" % infile)
                            except:
                                pass
    
    print('end of execute..Total Files:%s'%format(i,',') + ', %s KB'%format(totalsize / 1024.0, ','))
    print('end ..')
    print(time.asctime(time.localtime(time.time())))
    sqlstr = 'select b.filename,a.md5,a.filesize from filemd5 a inner join filemd5 b on a.md5=b.md5 '
    sqlstr += ' where a.filename in ( SELECT filename FROM filemd5 group by md5  having count (*) >= 2 order by filesize )'
    try:
        cursor = conn.execute(sqlstr)
        for rows in cursor:
            print("File:{} MD5:{} filesize:{}".format(rows[0], rows[1], format(rows[2], ',')))
            print('*' * 50)
    except:
        pass
    
    conn.close()

