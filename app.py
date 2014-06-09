#!/usr/bin/env python

import os
import platform
import sys
import wx
from wx import xrc
from unicode_table import toAscii
from m3u import M3UReader, M3UWriter
from ConfigParser import SafeConfigParser

MAX_ARTIST = 21

APP_DIR = sys.path[0]
if os.path.isfile(APP_DIR):  #py2exe/py2app
  APP_DIR = os.path.dirname(APP_DIR)
  
SOURCE_WIN = 'C:\\DOCUME~1\\RACHEL~1\\Desktop\\ZML\\Grooves.m3u'
DEST_WIN   = 'C:\\DOCUME~1\\RACHEL~1\\Desktop\\ZML\\Output'
SOURCE_MAC = ''
DEST_MAC   = ''

class SettingsFrame():
  def __init__(self, app, parent):
    self.app = app
    
    self.config_dir = wx.StandardPaths.Get().GetUserDataDir()
    if not os.path.isdir(self.config_dir):
      os.makedirs(self.config_dir)
    
    dialogxrc = xrc.XmlResource(os.path.join(APP_DIR, 'settings.xrc'))
    # note: sometimes doing the os.path.join with APP_DIR seems to kill xrc.
    #       I have no idea why but try without it if you're having problems.

    self.dlg = dialogxrc.LoadDialog(parent, 'dlgSettings')

    # Set events and initial control values
    self.getControl('btnSaveSettings').Bind(wx.EVT_BUTTON, self.onSaveSettings)
    self.getControl('btnCopy').Bind(wx.EVT_BUTTON, self.onCopy)
    self.getControl('btnClose').Bind(wx.EVT_BUTTON, self.onClose)
    self.dlg.Bind(wx.EVT_CLOSE, self.onClose)
    
    self.getControl('btnPlaylistBrowse').Bind(wx.EVT_BUTTON, self.onPlaylistBrowse)
    self.getControl('btnLibraryBrowse').Bind(wx.EVT_BUTTON, self.onLibraryBrowse)
    self.getControl('btnDestBrowse').Bind(wx.EVT_BUTTON, self.onDestBrowse)
    
    # todo: store these in a prefs/history file
    source_file = SOURCE_MAC
    dest_dir = DEST_MAC
    if platform.system() == 'Windows':
    	source_file = SOURCE_WIN
    	dest_dir = DEST_WIN
    	
    self.getControl('rbSourcePlaylist').SetValue(True)
    self.getControl('playlistPath').SetValue(source_file)
    self.getControl('destPath').SetValue(dest_dir)  
    self.getControl('rbDestFolder').SetValue(True)
    self.readSettings('global.ini')
    
  def readSettings(self, fname):
    fpath = os.path.join(self.config_dir, fname)
    if not os.path.exists(fpath):
      fpath = os.path.join(APP_DIR, fname)
      if not os.path.exists(fpath):
        print("no %s settings file found" % fname)
        return False
    
    parser = SafeConfigParser()
    parser.read(fpath)
    if not (parser.has_section('source') and parser.has_section('destination')):
      return False
      
    source_type = parser.get('source', 'type')
    if source_type == 'playlist':
      self.getControl('rbSourcePlaylist').SetValue(True)
    else:
      self.getControl('rbSourceFolder').SetValue(True)
    playlist_path = parser.get('source', 'playlist_path')
    self.getControl('playlistPath').SetValue(playlist_path)
    library_path = parser.get('source', 'library_path')
    self.getControl('libraryPath').SetValue(library_path)
    copy_method = parser.get('destination', 'copy_method')
    if copy_method == 'tree':
      self.getControl('rbDestTree').SetValue(True)
    else:
      self.getControl('rbDestFolder').SetValue(True)
    dest_path = parser.get('destination', 'dest_path')
    self.getControl('destPath').SetValue(dest_path)

    try:
      self.last_settings = parser.get('global', 'last_settings')
    except:
      self.last_settings = None

    print("settings loaded from %s" % fname)
    return True

  def saveSettings_(self, f, last_settings):
    parser = SafeConfigParser()
    parser.add_section('global')
    parser.set('global', 'last_settings', last_settings)
    parser.add_section('source')
    source_type = 'playlist'
    if self.getControl('rbSourceFolder').GetValue():
      source_type = 'library'
    parser.set('source', 'type', source_type)
    parser.set('source', 'playlist_path', self.getControl('playlistPath').GetValue())
    parser.set('source', 'library_path', self.getControl('libraryPath').GetValue())
    parser.add_section('destination')
    copy_method = 'folder'
    if self.getControl('rbDestTree').GetValue():
      copy_method = 'tree'
    parser.set('destination', 'copy_method', copy_method)
    parser.set('destination', 'dest_path', self.getControl('destPath').GetValue())
    parser.write(f)
    return True
  
  def saveSettingsGlobal(self, last_settings):
    fname = os.path.join(APP_DIR, 'global.ini')
    print("global settings file %s" % fname)
    f = open(fname, 'w')
    if not f:
      return False
    did_save = self.saveSettings_(f, last_settings)
    f.close()
    return did_save
    
  def saveSettings(self, fname):
    fname = os.path.realpath(os.path.join(self.config_dir, fname))
    print("user settings file %s" % fname)
    f = open(fname, 'w')
    if not f:
      return False
    did_save = self.saveSettings_(f, fname)
    f.close()
    if not did_save:
      return False
    self.last_settings = fname
    return self.saveSettingsGlobal(fname)
    
  def getControl(self, xmlid):
    '''Retrieves the given control (within a dialog) by its xmlid'''
    control = self.dlg.FindWindowById(xrc.XRCID(xmlid))
    if control == None and hasattr(self.dlg, 'GetMenuBar') and self.dlg.GetMenuBar() != None:  # see if on the menubar
      control = self.dlg.GetMenuBar().FindItemById(xrc.XRCID(xmlid))
    assert control != None, 'Programming error: a control with xml id ' + xmlid + ' was not found.'
    return control

  def onAbout(self, e):
    # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
    dlg = wx.MessageDialog(self.dlg, "Copies files", "About Playlist Manager", wx.OK)
    dlg.ShowModal() # Show it
    dlg.Destroy() # finally destroy it when finished.

  # todo
  def onSaveSettings(self, e):
    fname = wx.FileSelector("Save settings as:", 
      default_filename='global.ini', default_path=self.config_dir, 
      wildcard="INI files (*.ini)|*.ini", flags=wx.FD_SAVE)
    if fname:
      self.saveSettings(fname)

  def messageDialog(self, msg):
    dlg = wx.MessageDialog(self.dlg, msg, "Error", wx.OK|wx.ICON_EXCLAMATION)
    dlg.ShowModal()
    dlg.Destroy()

  def onCopy(self, e):
    dest = self.getControl('destPath').GetValue()
    if os.path.isdir(dest):
      copyTree = self.getControl('rbDestTree').GetValue()
      playlist = self.getControl('rbSourcePlaylist').GetValue()
      if playlist:
        source = self.getControl('playlistPath').GetValue()
        if os.path.isfile(source):
          self.app.copyPlaylist(source, dest, copyTree)
        else:
          self.messageDialog("Playlist file is not valid.")
      else:
        source = self.getControl('libraryPath').GetValue()
        if os.path.isdir(source):
          self.app.copyLibrary(source, dest, copyTree)
        else:
          self.messageDialog("Library folder is not valid.")
    else:
      self.messageDialog("Destination folder is not valid.")

  def onClose(self, e):
    confirmDlg = wx.MessageDialog(self.dlg, "Exit the program?", "Exit", wx.YES_NO|wx.ICON_QUESTION)
    if confirmDlg.ShowModal() == wx.ID_YES:
      self.dlg.Destroy()  # frame
    confirmDlg.Destroy()

  def onExit(self, e):
    self.Close(True)  # Close the frame.
    
  def onPlaylistBrowse(self, event):
    '''Responds to the 'Browse...' button'''
    source = self.getControl('playlistPath').GetValue()
    newSource = wx.FileSelector('Please select the m3u playlist file:', source)
    if newSource:
      self.getControl('playlistPath').SetValue(newSource)
    
  def onLibraryBrowse(self, event):
    '''Responds to the 'Browse...' button'''
    source = self.getControl('libraryPath').GetValue()
    newSource = wx.DirSelector('Please select the audio library folder:', source)
    if newSource:
      self.getControl('libraryPath').SetValue(newSource)
      
  def onDestBrowse(self, event):
    '''Responds to the 'Browse...' button'''
    dest = self.getControl('destPath').GetValue()
    newDest = wx.DirSelector('Please select the folder to save to:', dest)
    if newDest:
      self.getControl('destPath').SetValue(newDest)

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

  def copyPlaylist(self, source, dest, copyTree):
    self.contents = ''
    usource = unicode(source)
    udest = unicode(dest)
    self.processM3U(usource, udest)

  def copyLibrary(self, source, dest, copyTree):
    self.contents = ''
    usource = unicode(source)
    udest = unicode(dest)
    self.processDir(usource, udest, copyTree)
    

    

# Startup and handle loop
app = PlaylistManagerApp()
app.MainLoop()
