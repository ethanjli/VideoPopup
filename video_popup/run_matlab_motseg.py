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

def execute_matlab(results_path, command_pool=None):
    args = subsequences.generate_matlab_command('addpath {}; try,  load results.mat; save_segmentation(\'{}\'), catch ME, getReport(ME), end;'.format(results_path, 'results.mat'))
    if command_pool is None:
        p = subprocess.Popen(args, cwd=results_path, env=subsequences.MATLAB_ENVIRONMENT)
        p.wait()
    else:
        command_pool.add(executor.ExternalCommand(*args, directory=results_path, environment=subsequences.MATLAB_ENVIRONMENT))

def main():
    parser = argparse.ArgumentParser()
    subsequences.add_subsequence_args(parser)
    args = parser.parse_args()

    command_pool = executor.concurrent.CommandPool()
    # Copy files to results
    for (subsequence, start, end, subsampling) in subsequences.generate_subsequences_from_args(args):
        results_path = os.path.join(subsequences._OUTPUT_PATH, str(start), 'MotionSegmentation')
        execute_matlab(results_path, command_pool)
    command_pool.run()

if __name__ == '__main__':
    main()
