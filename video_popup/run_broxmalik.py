#!/usr/bin/env python
import os
import shutil
import subprocess
import errno
import re
import argparse

import executor
import executor.concurrent

BM_PATH = '/home/cvfish/Work/code/bitbucket/video_popup/libs/BroxMalik/trackingLinux64/tracking'

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

def file_names(parent_path, file_prefix='', file_suffix=''):
    """A generator of file names with the specified prefix and suffix in the specified directory.
    Output is naturally sorted, so numbers are in ascending order.
    """
    for path in sorted(os.listdir(parent_path), key=natural_keys):
        file_name = os.path.basename(path)
        if file_name.startswith(file_prefix) and file_name.endswith(file_suffix):
            yield file_name

# OWN FUNCTIONS

def copy_image_files(parent_dir, target_folder_path, image_filenames):
    make_dir_path(target_folder_path)
    for image_path in image_filenames:
        shutil.copyfile(os.path.join(parent_dir, image_path), os.path.join(target_folder_path, image_path))

def convert_images(folder_path):
    p = subprocess.Popen(['mogrify', '-format', 'ppm', '*.jpg'], cwd=folder_path)
    p.wait()

def make_bm_file(results_folder_path, image_filenames):
    make_dir_path(results_folder_path)
    lines = [os.path.splitext(image_filename)[0] + '.ppm'
            for image_filename in image_filenames]
    with open(os.path.join(results_folder_path, 'broxmalik.bmf'), 'w') as f:
        f.write(str(len(image_filenames)) + ' 1\n')
        f.write('\n'.join(lines))

def execute_broxmalik(results_folder_path, num_images, size, command_pool):
    args = [BM_PATH, './broxmalik.bmf', '0', str(num_images), str(size)]
    command_pool.add(executor.ExternalCommand(*args, directory=results_folder_path))

def process_images(parent_dir, folder_suffix, image_filenames, bm_size, command_pool):
    results_folder = os.path.join(parent_dir, 'broxmalik_Size' + str(bm_size) + '_' + folder_suffix)
    copy_image_files(parent_dir, os.path.join(parent_dir, 'subsequence_' + folder_suffix), image_filenames)
    copy_image_files(parent_dir, results_folder, image_filenames)
    convert_images(results_folder)
    make_bm_file(results_folder, image_filenames)
    execute_broxmalik(results_folder, len(image_filenames), bm_size, command_pool)

def generate_subsequences(sequence, length, subsampling, step, start, end):
    if step == 0:
        step = length * subsampling
    indices = range(len(sequence))
    subsequence_start_indices = indices[start:len(indices):step]
    for subsequence_start_index in subsequence_start_indices:
        subsequence_end_index = min(subsequence_start_index + subsampling * length, len(sequence) - end)
        subsequence = sequence[subsequence_start_index:subsequence_end_index:subsampling]
        yield (subsequence, subsequence_start_index, subsequence_end_index, subsampling)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', type=str, help='path of directory containing input images')
    parser.add_argument('--size', type=int, help='broxmalik step size', default=2)
    parser.add_argument('--length', type=int, help='number of frames per subsequence', default=8)
    parser.add_argument('--subsampling', type=int, help='number of frames to ignore between frames in each subsequence', default=10)
    parser.add_argument('--step', type=int, help='number of frames between the first frames of consecutive subsequences, default is --length.', default=0)
    parser.add_argument('--start', type=int, help='number of frames to ignore before the first frame of the first subsequence', default=0)
    parser.add_argument('--end', type=int, help='number of frames to ignore before the last frame of the last subsequence and the end of the sequence', default=0)
    args = parser.parse_args()

    all_images = list(file_names(args.dir, file_suffix='.jpg'))
    command_pool = executor.concurrent.CommandPool()
    for (subsequence, start, end, subsampling) in generate_subsequences(all_images, args.length, args.subsampling, args.step, args.start, args.end):
        suffix = 'start{}_length{}_subsampling{}'.format(start, args.length, subsampling)
        print suffix, subsequence
        process_images(args.dir, suffix, subsequence, args.size, command_pool)
    command_pool.run()

if __name__ == '__main__':
    main()
