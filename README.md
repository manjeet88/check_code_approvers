check_code_approvers
---------------------


Required: Python3

Imports: collections, argparse, pathlib


Assumptions:

    - cmd line tool is always run from the repo_root

    - case sensitive owners and dependencies

    - OWNERS file will be present inside
        at least one of the subdirectories

    - DEPENDENCIES file will have valid paths

To run the tool from the command line as a command:

    - Make the file an executable by adding execute permission
        chmod a+x

    - Strip of the file extension and copy the file to /usr/local/bin

    - A distributable binary can be created using a tool
        such as pyinstaller and distributing the whole dir 'dist'
