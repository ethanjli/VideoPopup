#!/usr/bin/env python
import os
import shutil
import subprocess
import errno
import re
import argparse

import executor
import executor.concurrent

_PACKAGE_PATH = os.path.dirname(os.path.abspath(__file__))
_ROOT_PATH = os.path.dirname(_PACKAGE_PATH)
_DATASETS_PATH = os.path.join(_ROOT_PATH, 'data')
_OUTPUT_PATH = os.path.join(_ROOT_PATH, 'results')
MATLAB_PATH = os.path.join(_ROOT_PATH, 'matlab')
MATLAB_ENVIRONMENT = os.environ.copy()
if 'LD_PRELOAD' not in MATLAB_ENVIRONMENT:
    MATLAB_ENVIRONMENT['LD_PRELOAD'] = '/usr/lib/x86_64-linux-gnu/libstdc++.so.6'
else:
    MATLAB_ENVIRONMENT['LD_PRELOAD'] = '/usr/lib/x86_64-linux-gnu/libstdc++.so.6:' + MATLAB_ENVIRONMENT['LD_PRELOAD']
MATLAB_COMMAND = '/usr/local/MATLAB/R2013a/bin/matlab'

# UTIL FUNCTIONS FROM CHARIOT

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    """Used for sorting in natural order.
    From http://nedbatchelder.com/blog/200712/human_sorting.html
    """
    return [atoi(c) for c in re.split('(\d+)', repr(text))]

def make_dir_path(path):
    """Ensures that the path is valid, creating directories when necessary."""
    try:
        os.makedirs(path)
    except OSError as e:
        if not(e.errno == errno.EEXIST and os.path.isdir(path)):
            raise

def rm_dir_path(path):
    """Ensures that the path does not exist, deleting the directory when necessary."""
    if os.path.exists(path):
        shutil.rmtree(path)

def file_names(parent_path, file_prefix='', file_suffix=''):
    """A generator of file names with the specified prefix and suffix in the specified directory.
    Output is naturally sorted, so numbers are in ascending order.
    """
    for path in sorted(os.listdir(parent_path), key=natural_keys):
        file_name = os.path.basename(path)
        if file_name.startswith(file_prefix) and file_name.endswith(file_suffix):
            yield file_name

# OWN FUNCTIONS

def generate_matlab_command(script):
    return [MATLAB_COMMAND, '-nodisplay', '-r', 'addpath ' + MATLAB_PATH + '; ' + script + '; exit']

def clear_directory(path):
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)

def copy_files(parent_path, file_prefix, file_suffix, destination_path):
    make_dir_path(destination_path)
    for filename in file_names(parent_path, file_prefix, file_suffix):
        shutil.copy(os.path.join(parent_path, filename), os.path.join(destination_path))

def generate_subsequences(sequence, length, subsampling, step, start, end):
    if step == 0:
        step = length * subsampling
    indices = range(len(sequence))
    subsequence_start_indices = indices[start:len(indices):step]
    for subsequence_start_index in subsequence_start_indices:
        subsequence_end_index = min(subsequence_start_index + subsampling * length, len(sequence) - end)
        subsequence = sequence[subsequence_start_index:subsequence_end_index:subsampling]
        yield (subsequence, subsequence_start_index, subsequence_end_index, subsampling)

def generate_subsequences_from_args(args):
    dir = os.path.join(_DATASETS_PATH, args.name)
    all_images = list(file_names(dir, file_suffix='.jpg'))
    return generate_subsequences(all_images, args.length, args.subsampling, args.step, args.start, args.end)

def results_folder_name(bm_size, start, length, subsampling):
    return 'broxmalik_Size{}_start{}_length{}_subsampling{}'.format(bm_size, start, length, subsampling)

def subsequence_folder_name(start, length, subsampling):
    return 'subsequence_start{}_length{}_subsampling{}'.format(start, length, subsampling)

def bm_results_folder_path(parent_dir, bm_results_folder_name):
    return os.path.join(parent_dir, bm_results_folder_name, 'broxmalikResults')

def motseg_results_folder_path(parent_dir, bm_results_folder_name, num_images):
    return os.path.join(parent_dir, bm_results_folder_name, 'broxmalikResults', 'f1t{}'.format(num_images), 'v1', 'vw10_nn10_k1_thresh100_max_occ2_op0_cw2.5', 'init200', 'mdl20000_pw3000_oc10_engine0_it5')

def add_subsequence_args(parser):
    parser.add_argument('name', type=str, help='name of image sequence of input images, e.g. "Log_C920_x1/3_downsampled"')
    parser.add_argument('--length', type=int, help='number of frames per subsequence', default=6)
    parser.add_argument('--subsampling', type=int, help='number of frames to ignore between frames in each subsequence', default=15)
    parser.add_argument('--step', type=int, help='number of frames between the first frames of consecutive subsequences, default is --length.', default=0)
    parser.add_argument('--start', type=int, help='number of frames to ignore before the first frame of the first subsequence', default=14)
    parser.add_argument('--end', type=int, help='number of frames to ignore before the last frame of the last subsequence and the end of the sequence', default=0)
    parser.add_argument('--size', type=int, help='broxmalik step size', default=2)

