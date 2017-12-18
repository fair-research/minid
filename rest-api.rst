REST API
==========

The following document describes the Minid REST API. 


User management
---------------

User operations act on a user object. The user object is represented by the following JSON: 

.. code-block:: json

  { 
    "email" : "" , 
    "name" : "", 
    "orchid" : ""
  }

**/user**

* [POST] Register a user.

  Input: 
  
  .. code-block:: json
   
      { 
        "email" : "" ,  [REQUIRED]
        "name" : "",    [REQUIRED]
        "orchid" : ""   [OPTIONAL]
      }
    
    
  Output: A User object.


* [PUT] Validate a registered user's code.

  Input:
  
  .. code-block:: json
   
    { 
      "email" : "" ,  [REQUIRED]
      "name" : "",    [REQUIRED]
      "orchid" : "",  [OPTIONAL]
      "code" : ""     [REQUIRED]
    }

  Output: A User object.
  

Minid management
----------------

Minid operations act on a Minid object that is represented with the following JSON: 

.. code-block:: json

    { 
      "identifier" : "",
      "checksum" : "",
      "titles" : [""],
      "locations" : [""],
      "status" : "",
      "obsoleted_by" : [""],
      "content_key" : "",
      "creator" : "",
      "created" : ""
    }
    
**/**

* [POST] Create a new Minid.

  Input:
  
  .. code-block:: json

    { 
      "checksum" : "" ,       [REQUIRED]
      "content_key" : "" ,    [OPTIONAL]
      "email" : "",           [REQUIRED]
      "code" : "",            [REQUIRED]
      "titles" : [""],        [REQUIRED]
      "locations" : [""],     [OPTIONAL]
    }
  
  
  Output: a Minid object.

**/<minid>** 

* [GET] Returns a Minid object for that Minid.

  Input: None
  
  Output: a Minid object.
  

* [PUT] Update a Minid. Only locations, titles, locations, status, and obsoleted_by can be updated. Note: this is a full put operation that requires submission of all prior information. The operation can only be performed by the creator of the Minid.
  
  Input:
  
  .. code-block:: json

    { 
      "email" : "" ,          [REQUIRED]
      "code" : "",            [REQUIRED]
      "titles" : [""],        [REQUIRED]
      "locations" : [""],     [OPTIONAL]
      "status" : "",          [OPTIONAL - 'ACTIVE' or 'TOMBSTONED']
      "obsoleted_by" : "",    [OPTIONAL - Valid minid]
    }
  
  
  Output: a Minid object.

   
**/<checksum>**
 
* [GET] Returns a Minid object for that checksum.
 
  Input: None
  
  Output: a Minid object.


