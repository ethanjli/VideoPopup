#!/usr/bin/env python
import os
import shutil
import subprocess
import errno
import re
import argparse

import executor
import executor.concurrent

import subsequences

def execute_matlab(image_path, results_path, command_pool=None):
    args = subsequences.generate_matlab_command('try, find_features(\'{}\', 100  ), catch ME, getReport(ME), end;'.format(image_path))
    if command_pool is None:
        p = subprocess.Popen(args, cwd=results_path, env=subsequences.MATLAB_ENVIRONMENT)
        p.wait()
    else:
        command_pool.add(executor.ExternalCommand(*args, directory=results_path, environment=subsequences.MATLAB_ENVIRONMENT))

def process_images(subsequence_folder, results_path, command_pool=None):
    subsequences.make_dir_path(results_path)
    for filename in subsequences.file_names(subsequence_folder, '', '.jpg'):
        execute_matlab(os.path.join(subsequence_folder, filename), results_path, command_pool)

def main(args):
    command_pool = executor.concurrent.CommandPool()
    for (subsequence, start, end, subsampling) in subsequences.generate_subsequences_from_args(args):
        subsequence_folder_name = subsequences.subsequence_folder_name(start, args.length, args.subsampling)
        dir = os.path.join(subsequences._DATASETS_PATH, args.name)
        subsequence_folder = os.path.join(dir, subsequence_folder_name)
        results_path = os.path.join(subsequences._OUTPUT_PATH, str(start), 'Input')
        process_images(subsequence_folder, results_path, command_pool)
    command_pool.run()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subsequences.add_subsequence_args(parser)
    args = parser.parse_args()

    main(args)
