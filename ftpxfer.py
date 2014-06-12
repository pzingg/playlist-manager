import ftputil
import os
import sys
from urlparse import urlparse

# host_info is a callable that returns a dict of server information for a 
# named host:
#    'login'       - ftp user to log in as
#    'password'    - ftp password
#    'ftp_root'    - ftp path on the host to the public html root
from servers import host_info

def ftp_upload(local_dir, saf_url):
  u = urlparse(saf_url)
  host = u.hostname
  
  info = host_info(host)
  if info is None:
    abort("Host %s not in database." % host)

  login         = info['login']
  password      = info['password']
  
  # remote_dir, no slash, e.g. /var/www/public_html/playlists/grooves
  remote_dir    = info['ftp_root'] + u.path
  if remote_dir.endswith('/'):
    remote_dir = remote_dir[:-1]
  if not local_dir.endswith(os.path.sep):
    local_dir += os.path.sep

  # Download some files from the login directory.
  with ftputil.FTPHost(host, login, password) as ftp_host:
    ulocal = unicode(local_dir)
    uremote = unicode(remote_dir)
    try:
      ftp_host.chdir(uremote)
    except:
      try:
        ftp_host.makedirs(uremote)
        ftp_host.chdir(uremote)
      except:
        raise
    print("remote_dir set to %r" % uremote)
    for name in os.listdir(ulocal):
      print("testing %r" % name)
      ext = os.path.splitext(name)[1].lower()
      if ext in ['.mp3', '.m3u', '.saf']:
        upath = os.path.join(ulocal, name)
        if os.path.isfile(upath):
          # remote name, local name, binary mode
          try:
            ftp_host.upload(upath, name)
            print("uploaded %r to %r" % (upath, name))
          except:
            print("failed to upload %r: %s" % (name, sys.exc_info()[0]))
