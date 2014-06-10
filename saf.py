#!/usr/bin/env python

import codecs

class SafWriter():
  def __init__(self, path, audio_url):
    self.path = path
    self.audio_url = audio_url
    self.default_encoding = 'latin-1' # Winamp on PC
    self.n = 0
    self.f = None
    
  def close(self):
    if self.f:
      self.f.write("NumberOfEntries=%d\r\n\r\n" % self.n)
      self.f.write("Version=2\r\n\r\n")
      self.f.write("<1.mtd>\r\n")
      self.f.write("url=%s\r\n\r\n" % self.audio_url)
      self.f.close()
      self.f = None

  def write(self, path, title, duration):
    if self.f is None:
      encoding = self.default_encoding
      self.f = codecs.open(self.path, 'w', encoding=encoding)
      self.f.write("<1.pls>\r\n")
      self.f.write("[playlist]\r\n\r\n")
    self.n += 1
    self.f.write("File%d=%s\r\n" % (self.n, path))
    self.f.write("Title%d=%s\r\n" % (self.n, title))
    self.f.write("Length%d=%s\r\n\r\n" % (self.n, duration))
    
if __name__ == '__main__':
  import m3u
  
  print("starting")
  reader = M3UReader('./playlist.m3u')
  saf = SafWriter('./contentupdate.saf', 'http://zinggmusiclab.com/zmlplayer/dwr/dwrcore')
  for item in reader:
    saf.write(item[1], item[2], item[3])
  saf.close()
