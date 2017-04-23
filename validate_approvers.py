#!/usr/bin/env python3


import argparse
from pathlib import Path
from collections import deque, defaultdict


class Approvals_Validator:
    '''
    Validator class encapsulating methods used to check
        if there are sufficient approvers
    '''
    def __init__(self):
        '''
        Initialize with a arg parser to parse cmd line inputs
        '''
        parser = argparse.ArgumentParser(
                    description='Validate approvals')
        parser.add_argument('-v', '--validators', nargs='+',
                    help='validators for files', required=True)
        parser.add_argument('-cf', '--changed-files', nargs='+',
                    help='changed files', required=True)
        args = parser.parse_args()
        self.input_validators = args.validators
        self.changed_files = args.changed_files

    def __get_enclosing_directory__(self, path):
        '''
        Returns the parent directory of a file or dir
        given the path
        '''
        return str(Path(path).parent)

    def __read_file_contents__(self, file_path):
        '''
        Returns a list of file contents given a file path
        '''
        contents = []
        if self.__file_exists__(file_path):
            with open(file_path, 'r') as input_file:
                for line in input_file:
                    contents.append(line.strip())
        return contents

    def __get_owners__(self, curr_listing):
        '''
        Returns a list of owners given the path of a file or dir
        Assuming OWNERS exists in one of the subdirectories in or
            inside repo_root
        '''
        owners = []
        curr_dir = self.__get_current_dir__(curr_listing)
        owners_file = '/OWNERS'

        # for a file, start looking for owners
        #   in enclosing directory
        # for a dir, start looking in itself
        while(not self.__file_exists__(str(curr_dir)
                                         + owners_file)):
            curr_dir = self.__get_enclosing_directory__(curr_dir)
        owners = self.__read_file_contents__(str(curr_dir)
                                                 + owners_file)
        return owners

    def __file_exists__(self, path):
        '''
        Checks if a given path exists and is a file
        '''
        exists = False
        if Path(path).is_file():
            exists = True
        return exists

    def __dir_exists__(self, path):
        '''
        Checks if a given path exists and is a dir
        '''
        exists = False
        if Path(path).is_dir():
            exists = True
        return exists

    def __get_dependencies__(self, parent_dir):
        '''
        Returns a list of dependencies if such a file exists
        '''
        dependencies = []
        dependencies_file = '/DEPENDENCIES'
        if self.__file_exists__(str(parent_dir)
                                    + dependencies_file):
            dependencies = self.__read_file_contents__(parent_dir
                                + dependencies_file)
        return dependencies

    def __get_current_dir__(self, listing):
        '''
        For a file, returns enclosing directory
        For a dir, returns itself
        '''
        curr_dir = ''
        if self.__file_exists__(listing):
            curr_dir = self.__get_enclosing_directory__(listing)
        elif self.__dir_exists__(listing):
            curr_dir = str(listing)
        return curr_dir

    def __get_required_approvers__(self):
        class ValidatorsDirsResult:
            '''
            The Result object has two values:
                - a dict mapping of owners of all affected
                    directories and the directories they can approve
                - a set of all affected directories/dependencies
            '''
            def __init__(self):
                self.validators_to_dir_map = defaultdict(set)
                self.dir_affected = set()

            def __str__(self):
                return ("Validators to Dir map: "
                            + str(self.validators_to_dir_map)
                            + "Dir Affected: "
                            + str(self.dir_affected))

            def update_result(self, owners, curr_dir):
                '''
                Updates the result instance with
                    the given list of owners and
                    the directory they can approve
                '''
                for owner in owners:
                    self.validators_to_dir_map[owner].add(curr_dir)
                self.dir_affected.add(curr_dir)

        stack_files = deque()

        # initial set of files to be reviewed
        if self.changed_files:
            stack_files.extend(self.changed_files)

        # result to be returned by method
        result = ValidatorsDirsResult()

        # keep track of visited dir to resolve circular dependencies
        visited = set()

        # while there are affected files/dir
        while stack_files:
            curr_listing = stack_files.popleft()
            curr_dir = self.__get_current_dir__(curr_listing)

            # using visited, check if dependencies and owners of
            # the current dir have been taken into account
            if curr_dir not in visited:
                visited.add(curr_dir)

                # find owners for each file
                owners = self.__get_owners__(curr_listing)

                # Update map with {owners:dir they can approve}
                # and add curr_dir to set of affected directories
                result.update_result(owners, curr_dir)

                # if there are dependencies, add to stack
                dependent_files = self.__get_dependencies__(curr_dir)
                if dependent_files:
                    stack_files.extend(dependent_files)
        return result

    def __has_sufficient_approvers__(self, validators_to_dir_map,
                                     dir_affected):
        '''
        Checks if there are sufficient approvers
            given a map of {owner: directories they can approve}
            and a set of all affected directories
        '''

        # for each validator given in the input, cross off the files
        # that they can approve using the set difference operation
        for validator in self.input_validators:
            dir_affected = (dir_affected
                            - validators_to_dir_map[validator])
        return False if dir_affected else True

    def validate_approvals(self):
        '''
        Public method used to validate_approvals
        '''
        result = self.__get_required_approvers__()
        return self.__has_sufficient_approvers__(
                    result.validators_to_dir_map,
                    result.dir_affected)

def main():
    validator = Approvals_Validator()
    sufficient = validator.validate_approvals()
    if sufficient:
        print("Approved")
    else:
        print("Insufficient approvals")

if __name__ == '__main__':
    main()

