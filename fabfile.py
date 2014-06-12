import os
from urlparse import urlparse

from fabric.api import settings
from fabric.utils import puts, warn, abort
from fabric.contrib.project import rsync_project

# host_info is a callable that returns a dict of server information for a 
# named host:
#    'login'          - user to log in as
#    'identity_file'  - private SSH key file
#    'public_root'    - path on the host to the public html root
from servers import host_info

# local_dir local directory, end with a slash, e.g. /playlist-manager/playlists/
# saf_url upload folder, eg. http://example.com/playlists/grooves
def upload(local_dir, saf_url):
  u = urlparse(saf_url)
  host = u.hostname
  
  info = host_info(host)
  if info is None:
    abort("Host %s not in database." % host)

  login         = info['login']
  identity_file = info['identity_file']
  
  # remote_dir, no slash, e.g. /var/www/public_html/playlists/grooves
  remote_dir    = info['public_root'] + u.path
  if remote_dir.endswith('/'):
    remote_dir = remote_dir[:-1]
  if not local_dir.endswith(os.path.sep):
    local_dir += os.path.sep
  
  ssh = '-2 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -l %s -i %s' % (login, identity_file)
  
  with settings(user=login, host_string=host):
    puts("local_dir %s" % local_dir)
    puts("remote_dir %s" % remote_dir)
    rsync_project(local_dir=local_dir, remote_dir=remote_dir, delete=True, ssh_opts=ssh, upload=True)
