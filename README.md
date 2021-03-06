Playlist Manager
================

A wxpython application to streamline Winamp-based playlists and 
audio libraries.

Manipulate music libraries
--------------------------

1. Rename music files to conform to 7-bit ASCII, with maximum string length.
2. Update .m3u playlist files to 7-bit ASCII
3. Produce playlist control files for other systems
4. Export playlists and source files to local folder
5. Sync exported files to remote production server

Future wishlist
---------------

6. Combine multiple playlists into one folder with single .saf file
7. Batch apply standard audio normalization and/or compression to music files
8. Batch apply ID3 metadata from online service
9. Create persistent song ID and version and store in ID3
10. Drag and drop playlist management with audio player
11. SQL- and JSON-based playlist system

Uploading files to production server
------------------------------------

Two methods for uploading. Fabric, python-based deployment library that
uses rysnc to copy files. On Windows, you should be able to install fabric
using ActiveState's pypm tool. Also, pre-built pycrypto modules can be 
installed.

- http://www.fabfile.org/index.html
- https://github.com/fabric/fabric
- http://docs.fabfile.org/en/1.4.0/installation.html
- http://www.voidspace.org.uk/python/modules.shtml#pycrypto

Second approach is the ftputil python library, since it's difficult to
install rsync on Windows.

- http://ftputil.sschwarzer.net/trac/wiki/Documentation

Requirements for Windows
------------------------

Here's what needs to be installed to get things working.

- ActiveState Python 2.7
- wxpython (prebuilt binaries)
- PyCrypto (prebuilt binaries)
- Fabric - pip install Fabric
- Cygwin - rsync, openssh, libssh and dependencies
