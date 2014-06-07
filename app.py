#!/usr/bin/env python

import os
import platform
import sys
import wx
from wx import xrc
from unicode_table import toAscii
from m3u import M3UReader, M3UWriter

MAX_ARTIST = 21

APPDIR = sys.path[0]
if os.path.isfile(APPDIR):  #py2exe/py2app
  APPDIR = os.path.dirname(APPDIR)
  
SOURCE_WIN = 'C:\\DOCUME~1\\RACHEL~1\\Desktop\\ZML\\Grooves.m3u'
DEST_WIN   = 'C:\\DOCUME~1\\RACHEL~1\\Desktop\\ZML\\Output'
SOURCE_MAC = ''
DEST_MAC   = ''

class SettingsFrame():
  def __init__(self, app, parent):
    self.app = app
    
    dialogxrc = xrc.XmlResource(os.path.join(APPDIR, 'settings.xrc'))
    # note: sometimes doing the os.path.join with APPDIR seems to kill xrc.
    #       I have no idea why but try without it if you're having problems.

    self.dlg = dialogxrc.LoadDialog(parent, 'settingsFrame')

    # Set events and initial control values
    self.dlg.Bind(wx.EVT_CLOSE, self.onClose)
    self.getControl('cancelButton').Bind(wx.EVT_BUTTON, self.onClose)
    self.getControl('copyButton').Bind(wx.EVT_BUTTON, self.onCopy)
    self.getControl('sourceButton').Bind(wx.EVT_BUTTON, self.onSourceButton)
    self.getControl('destButton').Bind(wx.EVT_BUTTON, self.onDestButton)
    
    # todo: store these in a prefs/history file
    source_file = SOURCE_MAC
    dest_dir = DEST_MAC
    if platform.system() == 'Windows':
    	source_file = SOURCE_WIN
    	dest_dir = DEST_WIN
    self.getControl('source').SetValue(source_file)
    self.getControl('dest').SetValue(dest_dir)  
    self.getControl('treeNo').SetValue(True)
    
  def getControl(self, xmlid):
    '''Retrieves the given control (within a dialog) by its xmlid'''
    control = self.dlg.FindWindowById(xrc.XRCID(xmlid))
    if control == None and self.dlg.GetMenuBar() != None:  # see if on the menubar
      control = self.dlg.GetMenuBar().FindItemById(xrc.XRCID(xmlid))
    assert control != None, 'Programming error: a control with xml id ' + xmlid + ' was not found.'
    return control

  def onAbout(self, e):
    # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
    dlg = wx.MessageDialog(self.dlg, "Copies files", "About Playlist Manager", wx.OK)
    dlg.ShowModal() # Show it
    dlg.Destroy() # finally destroy it when finished.

  def onClose(self, e):
    confirmDlg = wx.MessageDialog(self.dlg, "Exit the program?", "Exit", wx.YES_NO | wx.ICON_QUESTION)
    if confirmDlg.ShowModal() == wx.ID_YES:
      self.dlg.Destroy()  # frame
    confirmDlg.Destroy()

  def onExit(self, e):
    self.Close(True)  # Close the frame.
    
  def onCopy(self, e):
    source = self.getControl('source').GetValue()
    dest = self.getControl('dest').GetValue()
    copyTree = self.getControl('treeYes').GetValue()
    self.app.copyFiles(source, dest, copyTree)

  def onSourceButton(self, event):
    '''Responds to the 'Browse...' button'''
    source = self.getControl('source').GetValue()
    newSource = wx.FileSelector('Please select an m3u file or a file in a directory to start with:', source)
    if newSource:
      self.getControl('source').SetValue(newSource)
    
  def onDestButton(self, event):
    '''Responds to the 'Browse...' button'''
    dest = self.getControl('dest').GetValue()
    newDest = wx.DirSelector('Please select the directory to save to:', dest)
    if newDest:
      self.getControl('dest').SetValue(newDest)

class PlaylistManagerApp(wx.App):
  '''Main application class'''
  def __init__(self):
    wx.App.__init__(self)
    self.contents = ''

  def OnInit(self):
    '''Sets everything up'''
    # set up the main frame of the app
    self.SetAppName('Playlist Manager')
    self.settingsFrame = SettingsFrame(self, None)
    self.settingsFrame.dlg.Show(True)
    return True

  def appendContents(self, s):
    sys.stderr.write(s + "\n")
    # self.contents += (s + "\n")
    # self.control.SetValue(self.contents)
    
  def normalizeTitle(self, line, maxArtist, maxName):
    destName = toAscii(line)
    try:
      artist, title = destName.split(u' - ', 1)
      artist_len = len(artist)
      if artist_len > maxArtist:
        artist_len = maxArtist
        artist = artist[0:artist_len]
      title_len = len(title)
      if title_len > maxName - (3 + artist_len):
        title_len = maxName - (3 + artist_len)
        title = title[0:title_len]
      destName = artist + u' - ' + title
    except:
      title = destName
      title_len = len(title)
      if title_len > maxName:
        title_len = maxName
        title = title[0:title_len]
      destName = title
    return destName

  def processFile(self, sourceName, sourceDir, destDir):
    basename, ext = os.path.splitext(sourceName)
    destName = self.normalizeTitle(basename, MAX_ARTIST, 45) + ext
    if destName != sourceName or destDir != sourceDir:
      self.appendContents("file: %r %r -> %r %r" % (sourceDir, sourceName, destDir, destName))  
    return destName

  def processM3U(self, source, destDir):
    m3u_name = os.path.basename(source)
    out_fname = os.path.join(destDir, m3u_name)
    m3u_in = M3UReader(source)
    m3u_out = M3UWriter(out_fname)
    for item in m3u_in:
      i, path, title, duration = item
      safeTitle = self.normalizeTitle(title, MAX_ARTIST, 49)
      sourceDir, sourceName = os.path.split(path)
      destName = self.processFile(sourceName, sourceDir, destDir)
      m3u_out.write(destName, safeTitle, duration)
    m3u_out.close()

  def processDir(self, source, dest, copyTree):
    self.source = source
    self.dest = dest
    destPath = dest
    sourceLen = len(source) + 1
    for sourcePath, dirs, files in os.walk(source):
      for sourceName in files:
        if ufname[-4:] == u'.mp3':
          if copyTree:
            rel = sourcePath[sourceLen:]
            if rel == u'':
              destPath = dest
            else:
              destPath = os.path.join(dest, rel)
          self.processFile(sourceName, sourcePath, destPath)

  def copyFiles(self, source, dest, copyTree):
    self.contents = ''
    usource = unicode(source)
    udest = unicode(dest)
    if usource[-4:] == u'.m3u':
      self.processM3U(usource, udest)
    else:
      udir = os.path.dirname(usource)
      self.processDir(udir, udest, copyTree)


# Startup and handle loop
app = PlaylistManagerApp()
app.MainLoop()
