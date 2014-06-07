#!/usr/bin/env python

import codecs
import os
import re

class M3UReader():
  def __init__(self, path):
    self.path = path
    self.default_encoding = 'latin-1' # Winamp on PC
    self.f = None
    self.m3u = re.compile(r'#EXTM3U')
    self.inf = re.compile(r'#EXTINF:([-]?\d+),(.+)')
    self.lno = 0
    self.i = 0
  
  def __iter__(self):
    return self
    
  def next(self):
    try:
      if self.f is None:
        encoding = self.default_encoding
        basename, ext = os.path.splitext(self.path)
        if ext.lower() == '.m3u8':
          encoding = 'utf-8'
        self.f = codecs.open(self.path, 'r', encoding=encoding)
        line = self.f.readline().rstrip()
        self.lno += 1
        if not re.match(self.m3u, line):
          print("no extm3u in %s at line %d" % (self.path, self.lno))
          raise StopIteration
      line = self.f.readline().rstrip()
      self.lno += 1
      if line == '':
        raise StopIteration
      m = re.match(self.inf, line)
      if not m:
        print("no extinf parsed for %s at line %d" % (self.path, self.lno))
        raise StopIteration
      duration = int(m.group(1))
      title = m.group(2)
      path = self.f.readline().rstrip()
      self.lno += 1
      self.i += 1
      return (self.i, path, title, duration)
    except:
      self.f.close()
      raise
      
class M3UWriter():
  def __init__(self, path):
    self.path = path
    self.default_encoding = 'latin-1' # Winamp on PC
    self.f = None
    
  def close(self):
    if self.f:
      self.f.close()

  def write(self, path, title, duration):
    if self.f is None:
      encoding = self.default_encoding
      basename, ext = os.path.splitext(self.path)
      if ext.lower() == '.m3u8':
        encoding = 'utf-8'
      self.f = codecs.open(self.path, 'w', encoding=encoding)
      self.f.write(u'#EXTM3U\r\n')
    self.f.write(u'#EXTINF:%d,%s\r\n' % (duration, title))
    self.f.write(u'%s\r\n' % path)
      
if __name__ == '__main__':
  print("starting")
  reader = M3UReader('./playlist.m3u')
  for item in reader:
    print("%d %r %s %d" % (item[0], item[1], item[2], item[3]))
