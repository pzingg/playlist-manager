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

DEBUG = True

def verifyDirectory(path):
  if not os.path.isdir(path):
    try:
      os.makedirs(path)
    except:
      return False
  return True
  
def relativeSubdirectory(base_path, directory):
  # adds a slash if it's not there
  base_path = os.path.normcase(os.path.join(os.path.realpath(base_path), ''))
  directory = os.path.normcase(os.path.join(os.path.realpath(directory), ''))
  print("checking directory %s startswith %s" % (directory, base_path))
  if directory.startswith(base_path):
    rel = directory[len(base_path):]
    return rel
  return None

class SettingsFrame():
  def __init__(self, app, parent):
    self.app = app
    
    self.config_dir = wx.StandardPaths.Get().GetUserDataDir()
    verifyDirectory(self.config_dir)
    
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
      self.getControl('rbSourceLibrary').SetValue(True)
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
    if self.getControl('rbSourceLibrary').GetValue():
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
      copy_tree = self.getControl('rbDestTree').GetValue()
      playlist = self.getControl('rbSourcePlaylist').GetValue()
      base_dir = self.getControl('libraryPath').GetValue()
      if playlist:
        source = self.getControl('playlistPath').GetValue()
        if os.path.isfile(source):
          if not copy_tree or base_dir == '':
            base_dir = os.path.dirname(source)
          if os.path.isdir(base_dir):
            self.app.copyPlaylist(source, base_dir, dest, copy_tree)
          else:
            self.messageDialog("Base folder is not valid.")
        else:
          self.messageDialog("Playlist file is not valid.")
      else:
        if os.path.isdir(base_dir):
          self.app.copyFolder(base_dir, dest, copy_tree)
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
    base_dir = self.getControl('libraryPath').GetValue()
    newSource = wx.DirSelector('Please select the audio library folder:', base_dir)
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
    dest_name = toAscii(line)
    try:
      artist, title = dest_name.split(u' - ', 1)
      artist_len = len(artist)
      if artist_len > maxArtist:
        artist_len = maxArtist
        artist = artist[0:artist_len]
      title_len = len(title)
      if title_len > maxName - (3 + artist_len):
        title_len = maxName - (3 + artist_len)
        title = title[0:title_len]
      dest_name = artist + u' - ' + title
    except:
      title = dest_name
      title_len = len(title)
      if title_len > maxName:
        title_len = maxName
        title = title[0:title_len]
      dest_name = title
    return dest_name

  def processFile(self, source_name, source_dir, base_dir, root_dir, dest_dir, copy_tree):
    source_dir = os.path.join(base_dir, source_dir)
    source_path = os.path.join(source_dir, source_name)
    # check that source file exists
    if not os.path.isfile(source_path):
      print("source file %s does not exist" % source_path)
      if not DEBUG:
        return None
    basename, ext = os.path.splitext(source_name)
    dest_name = self.normalizeTitle(basename, MAX_ARTIST, 45) + ext
    rel_dir = dest_dir
    if copy_tree:
      # check that the file to be copied is in a subdirectory of the library
      rel_dir = relativeSubdirectory(root_dir, source_dir)
      if rel_dir is None:
        print("%s is not a subdirectory of %s" % (source_dir, root_dir))
        if not DEBUG:
          return None
      else:
        dest_dir = os.path.join(dest_dir, rel_dir)
    # check that dest dir exists, create if not
    if not verifyDirectory(dest_dir):
      print("could not create dest dir %s" % dest_dir)
      if not DEBUG:
        return None
    # copy file
    dest_path = os.path.join(dest_dir, dest_name)
    try:
      shutil.copy2(source_path, dest_path)
    except:
      print("could not copy file from %s to %s" % (source_path, dest_path))
      if not DEBUG:
        return None
    self.appendContents("file: %s %s -> %s %s" % (source_dir, source_name, dest_dir, dest_name))  
    # return updated path for m3u to write
    if copy_tree:
      return os.path.join(rel_dir, dest_name)
    return dest_name

  def processPlaylist(self, source, root_dir, dest_dir, copy_tree):
    base_dir, m3u_name = os.path.split(source)
    verifyDirectory(dest_dir)
    out_fname = os.path.join(dest_dir, m3u_name)
    m3u_in = M3UReader(source)
    m3u_out = M3UWriter(out_fname)
    for item in m3u_in:
      i, path, title, duration = item
      source_dir, source_name = os.path.split(path)
      dest_name = self.processFile(source_name, source_dir, base_dir, root_dir, dest_dir, copy_tree)
      if dest_name:
        safe_title = self.normalizeTitle(title, MAX_ARTIST, 49)
        m3u_out.write(dest_name, safe_title, duration)
    m3u_out.close()

  def processDir(self, source, dest, copy_tree):
    base_dir = source
    dest_dir = dest
    for source_dir, dirs, files in os.walk(source):
      for source_name in files:
        if ufname[-4:] == u'.mp3':
          self.processFile(source_name, source_dir, base_dir, base_dir, dest_dir, copy_tree)

  def copyPlaylist(self, source, root, dest, copy_tree):
    self.contents = ''
    usource = unicode(source)
    uroot = unicode(root)
    udest = unicode(dest)
    self.processPlaylist(usource, uroot, udest, copy_tree)

  def copyFolder(self, source, dest, copy_tree):
    self.contents = ''
    usource = unicode(source)
    udest = unicode(dest)
    self.processDir(usource, udest, copy_tree)

# Startup and handle loop
app = PlaylistManagerApp()
app.MainLoop()
