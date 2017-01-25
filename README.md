# Docker Image For Managing Big Data

Administers a set of docker containers - one for each student of csv file.

## Overview

This project assumes that a teacher (or operator) runs one docker container of
a certain image for each student in a course. The containers are distributed over
a set of hosts.

[![Overview](overview.png)](http://interactive.blockdiag.com/?compression=deflate&src=eJxtkMEKwjAMhu99irK7B-dFGPNFRCRrs62sNCPNEBXf3QxhHrpj_nz5_yRdJDf5AIN9G-KASUACJdvamVgYgjTGYw9LlHtPSXJ4oTbPjTFDnhnB5xFR7OFiEwl2RJO9RugwttVjQKluShYdQXAj8jayUhukViNlOW4052dye0hdSqdSSo35-Wnt9AQICfnv7vUBugovaY0oyXpP1JjPF9UDa7A)

## Running A Course

To run a course, one container has to be started per user. This is
achieved by creating a google spread sheet file containing all users
(teachers and students). The schema with some sample data looks as
follows (see [here](https://docs.google.com/spreadsheets/d/1-B2VSvY8iyBNxeTRmxve7-283pKBC56RSuB6_clDhVw/edit?usp=sharing) for a template):

| SNumber | Name   | LastName | Email | url                                 | server     | port     | Password | Admin |
| ------- | ----   | -------- | ----  | -------                             | ---------- | -------- | -------- | ------ |
| mXXXXXX | John   | Smith    | XXX   | http://farm01.ewi.utwente.nl:20000/ | farm01     | 20000    | W7pyhH0f | FALSE |
| sYYYYYY | Babara | Smith    | YYYY  | http://farm03.ewi.utwente.nl:20001/ | farm03     | 20001    | IBCsaFwu | FALSE |

This spreadsheet can be initially filled by importing a userlist from
blackboard. The fields without non-obvious meaning are:

* ``server``: the server the notebook of this user should be run
* ``port``: the external port on which the notebook container will listen
* ``url``: A string function (using CONCAT()) that forms an URL suitable to be mailed to students.
* ``Password``: The password for the notebook (see below).
* ``Admin``: TRUE/FALSE, whether the user should be a admin user.  

To generate the password for ``Password`` the following spreadsheet
function was used (Using Tools / Script Editor)

    function genPass(l) {
      var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
      var text = "";
      for( var i=0; i < l; i++ ) 
          text += possible.charAt(Math.floor(Math.random() * possible.length));

       return text;
    }

Once the spreadsheet is created, two files have to be edited:

* ``hosts``: this file contains all the hosts on which docker containers will run.
* ``sync.sh``: this script that starts the docker containers by copying the spreadsheet 
  and the script ``bin/manage_nb.py`` to all hosts and then executing the script.

If the script ``sync.sh`` is invoked it starts the containers on the hosts indicated in the mbd_server
field. 

Once the containers are started, the users should be informed using
the downloaded csv file. In the past, the Thunderbird add-on Mail
Merge was used.

## Creating Assignments

To understand how assignments can be created, one has to understand the directory structure, where files for this course are stored, which is the following:

<pre>
├── bin                         these are utility scripts
│   ├── build.sh
│   ├── create_release.sh
│   ├── distribute_release.sh
│   ├── insertTOC.py
│   ├── manage_nbs.py
│   └── removeSolutions.py
├── students                    this folder contains one folder per student, containing all his submissions.
│   ├── sXXXXX
│   ├── sYYYYY
├── teacher
│   ├── assignments             this folder contains a version of the assignments that is ready to be distributed to students
│   │   ├── assignment1
│   │   └── assignment2
│   └── solutions               this folder contains assignments together with their solutions.
│       ├── assignment1
│       └── assignment2
└── users.csv
</pre>

To produce an assignment you can follow this procedure:

1. Create a folder in ``teacher/solutions``, say ``assignment3``. Solutions to exercies should be enclosed in ###BEGIN SOLUTION ###END SOLUTION markers.
2. Inside an administrator notebook open a termina, and call ``bin/create_release.sh assignment3``, which first removes all solutions between the given markers and saves these files under ``teacher/assignments/assignment3``.
3. Call ``bin/distribute_release.sh assignment3``, which copies ``teacher/assignments/assignment3`` into the directory of each student under ``students/``.
