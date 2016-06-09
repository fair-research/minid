![minid](https://raw.githubusercontent.com/ini-bdds/minid/master/minid_server/static/images/minid-logo.png)

This project aims to create a Minimal Viable Identifier (MVI). An identifier that is sufficiently simple to make creation and use trivial, while still having enough substance to make data easily findable, accessible, interoperable, and reusable (FAIR). 

## Installation
The CLI can be installed using Python setuptools. 

## Configuration
Before using the API you first need to validate your email address. Enter the following command: 

`minid.py --register_user --email <email> --name <name> [--orcid <orcid>]`

A unique code will be sent to your email address. You must present this code along with your 
email address when accessing the API. As a convenience you can specify this information in 
a minid configuration file (`~/.minid/minid-config.cfg`)

```
[general]
minid_server: http://minid.bd2k.org/minid
user: <Name>
email: <Email>
orcid: <optional Orcid>
code: <Code>
```

## Usage

The CLI supports the following simple operations (Note: the test flag will create names in a test namespace that will be removed periodically, remove the test flag for creating production minids.): 

* Create a new identifier: `minid.py --test --register [--title <title>] <file_name>`
* Retrieve metadata about a file: `minid.py --test <file_name>` 
* Retrieve metadata about an identifier: `minid.py --test <identifier>`
* Update metadata about an identifier: `minid.py --test --update [--title <title>] [--status <status>] [--obsoleted_by <minid>] [--locations <loc1> <loc2>] <identifier>`
*  View all minid options: `minid.py -h`

Landing pages are accessible via the minid website: minid.bd2k.org/minid/landingpage/<identifier>. 

## More information
More information about the project can be found at: [minid.bd2k.org](http://minid.bd2k.org/)
