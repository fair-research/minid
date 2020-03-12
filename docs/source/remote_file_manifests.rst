File Manifest Format
--------------------
Minids can only be assigned to a single file. In order to assign a minid to a collection of files we recommend using a `BDBag <https://github.com/ini-bdds/bdbag>`_ or the minid file manifest format.

The minid file manifest format is a JSON-based format that enumerates a list of files as JSON objects that have the following attributes:

* length: The length of the file in bytes.

* filename: The filename (or path) relative to the manifest file.

* One or more (only one of each) of the following `algorithm:checksum` key-value pairs:

  * md5:<md5 hex value>

  * sha256:<sha256 hex value>

  * sha512:<sha512 hex value>

* url: the URL to the file.

The manifest may be used to create a minid for a collection of files or alternatively as input to the minid batch-register command.

Below is a sample file manifest configuration file::

  [
      {
          "length":321,
          "filename":"file1.txt",
          "md5":"5bbf5a52328e7439ae6e719dfe712200",
          "sha256":"2c8b08da5ce60398e1f19af0e5dccc744df274b826abe585eaba68c525434806",
          "url" : "globus://ddb59aef-6d04-11e5-ba46-22000b92c6ec/share/godata/file1.txt"
      },
      {
          "length": 632860,
          "filename": "minid_v0.1_Nov_2015.pdf",
          "sha256": "cacc1abf711425d3c554277a5989df269cefaa906d27f1aaa72205d30224ed5f",
          "url" : "http://bd2k.ini.usc.edu/assets/all-hands-meeting/minid_v0.1_Nov_2015.pdf"
      }
  ]

