#!/usr/bin/python3

'''
How do i know what is the root directory? is the cmd line tool run from inside the dir?
'''

import sys
import argparse
from pathlib import Path
from collections import deque, defaultdict


class Approvals_Validator:

    def __init__(self):
        parser = argparse.ArgumentParser(description='Validate approvals')
        parser.add_argument('-v', '--validators', nargs='+',
                            help='validators for files')
        parser.add_argument('-cf', '--changed-files', nargs='+',
                            help='changed files')
        args = parser.parse_args()
        self.input_validators = args.validators
        self.changed_files = args.changed_files

    def __get_enclosing_directory__(self, path):
        '''
        returns the parent directory of a file or dir
        given the path
        '''
        return str(Path(path).parent)

    def __read_file_contents__(self, file_path):
        contents = []
        with open(file_path, 'r') as ip_file:
            for line in ip_file:
                contents.append(line.strip())
        return contents

    def __get_owners__(self, curr_listing):
        owners = []
        curr_dir = self.__get_current_dir__(curr_listing)
        owners_file = '/OWNERS'

        # for a file, start looking for owners
        #   in enclosing directory
        # for a dir, start looking in itself
        while(not self.__file_exists__(str(curr_dir)+str(owners_file))):
            curr_dir = self.__get_enclosing_directory__(curr_dir)
        owners = self.__read_file_contents__(str(curr_dir)+owners_file)
        return owners

    def __file_exists__(self, path):
        exists = False
        if Path(path).is_file():
            exists = True
        return exists

    def __dir_exists__(self, path):
        exists = False
        if Path(path).is_dir():
            exists = True
        return exists

    def __get_dependencies__(self, parent_dir, dependencies_file):
        dependencies = []
        if self.__file_exists__(str(parent_dir)+str(dependencies_file)):
            dependencies = self.__read_file_contents__(
                                parent_dir+dependencies_file)
        return dependencies

    def __get_current_dir__(self, listing):
        '''
        for a file, return enclosing directory
        for a dir, return itself
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
                a dict mapping of owners of all affected
                 directories and the directories they can approve &
                a set of all affected directories/dependencies
            '''
            def __init__(self):
                self.validators_to_dir_map = defaultdict(set)
                self.dir_affected = set()

            def __str__(self):
                return ("validators to dir map:"+str(self.validators_to_dir_map)+"dir affected:"+str(self.dir_affected))

            def update_result(self, owners, curr_dir):
                for owner in owners:
                    self.validators_to_dir_map[owner].add(curr_dir)
                self.dir_affected.add(curr_dir)

        stack_files = deque()
        required_approvers = defaultdict(list)
        # initial set of files to be reviewed
        stack_files.extend(self.changed_files)
        result = ValidatorsDirsResult()
        visited = set()

        while stack_files:
            # print("stack:", stack_files)
            curr_listing = stack_files.popleft()
            print("curr_listing:", curr_listing)
            curr_dir = self.__get_current_dir__(curr_listing)
            # parent_dir = self.__get_enclosing_directory__(curr_listing)
            print("curr_dir:", curr_dir)
            # use visited to keep track of visited directories
            if curr_dir not in visited:
                visited.add(curr_dir)
                print("99", stack_files, visited)
                # find owners for each file
                # and add to required approvers
                owners = self.__get_owners__(curr_listing)
                print("owners:", owners)
                result.update_result(owners, curr_dir)

                # if there are dependencies, add to stack
                dependencies_file = '/DEPENDENCIES'
                dependent_files = self.__get_dependencies__(curr_dir, dependencies_file)
                print("dep:", dependent_files)
                if dependent_files:
                    stack_files.extend(dependent_files)
            print("\n")
        return result

    def __has_sufficient_approvers__(self, required_approvers, dir_to_notify):
        print("\n")
        for validator in self.input_validators:
            dir_to_notify = set(dir_to_notify) - set(required_approvers[validator])
            print("131", dir_to_notify)
        return False if dir_to_notify else True

    def validate_approvals(self):
        result = self.__get_required_approvers__()
        print(result)
        return self.__has_sufficient_approvers__(result.validators_to_dir_map, result.dir_affected)

def main():
    validator = Approvals_Validator()
    sufficient = validator.validate_approvals()
    if sufficient:
        print("Approved")
    else:
        print("Insufficient approvals")

if __name__ == '__main__':
    main()

