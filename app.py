#!/usr/bin/env python

import os
import wx
from unicode_table import toAscii

MAX_ARTIST = 21
MAX_NAME = 45

class MainWindow(wx.Frame):
  def __init__(self, parent, title):
    wx.Frame.__init__(self, parent, title=title, size=(200,100))
    self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)
    self.contents = ''
    self.CreateStatusBar() # A StatusBar in the bottom of the window

    # Setting up the menu.
    filemenu = wx.Menu()

    # wx.ID_ABOUT and wx.ID_EXIT are standard ids provided by wxWidgets.
    menuAbout = filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
    menuOpen = filemenu.Append(wx.ID_OPEN, "&Open"," Select a directory")
    menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")

    # Creating the menubar.
    menuBar = wx.MenuBar()
    menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
    self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

    # Set events.
    self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
    self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
    self.Bind(wx.EVT_MENU, self.OnExit, menuExit)

    self.Show(True)
    
  def appendContents(self, s):
    self.contents += (s + "\n")
    self.control.SetValue(self.contents)
    
  def processFile(self, path, ufname):
    basename, ext = os.path.splitext(ufname)
    unewname = toAscii(basename)
    try:
      artist, title = unewname.split(u' - ')
      artist_len = len(artist)
      if artist_len > MAX_ARTIST:
        artist_len = MAX_ARTIST
        artist = artist[0:artist_len]
      title_len = len(title)
      if title_len > MAX_NAME - (3 + artist_len):
        title_len = MAX_NAME - (3 + artist_len)
        title = title[0:title_len]
      unewname = artist + u' - ' + title + ext
    except:
      title = unewname
      title_len = len(title)
      if title_len > MAX_NAME:
        title_len = MAX_NAME
        title = title[0:title_len]
      unewname = title + ext
    if unewname != ufname:
      self.appendContents("filename: %r -> %r" % (ufname, unewname))  
    
  def processDirectory(self, rootdir):
    for upath, udirs, ufiles in os.walk(unicode(rootdir)):
      for ufname in ufiles:
        if ufname[-4:] == u'.mp3':
          self.processFile(upath, ufname)

  def OnOpen(self, e):
    """ Select a directory"""
    self.dirname = ''
    dlg = wx.FileDialog(self, "Choose the top level directory by picking a file or folder in it", self.dirname, "", "*.*", wx.OPEN)
    if dlg.ShowModal() == wx.ID_OK:
      self.filename = dlg.GetFilename()
      self.dirname = dlg.GetDirectory()
      # f = open(os.path.join(self.dirname, self.filename), 'r')
      self.appendContents(self.dirname)
      self.processDirectory(self.dirname)
      # f.close()
    dlg.Destroy()  
    
  def OnAbout(self, e):
    # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
    dlg = wx.MessageDialog( self, "A small text editor", "About Sample Editor", wx.OK)
    dlg.ShowModal() # Show it
    dlg.Destroy() # finally destroy it when finished.

  def OnExit(self, e):
    self.Close(True)  # Close the frame.

app = wx.App(False)
frame = MainWindow(None, "Sample application")
app.MainLoop()

