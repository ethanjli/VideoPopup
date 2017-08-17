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

BM_PATH = '/home/cvfish/Work/code/bitbucket/video_popup/libs/BroxMalik/trackingLinux64/tracking'

def copy_image_files(parent_dir, target_folder_path, image_filenames):
    subsequences.make_dir_path(target_folder_path)
    for image_path in image_filenames:
        shutil.copyfile(os.path.join(parent_dir, image_path), os.path.join(target_folder_path, image_path))

def convert_images(folder_path):
    p = subprocess.Popen(['mogrify', '-format', 'ppm', '*.jpg'], cwd=folder_path)
    p.wait()

def make_bm_file(results_folder_path, image_filenames):
    subsequences.make_dir_path(results_folder_path)
    lines = [os.path.splitext(image_filename)[0] + '.ppm'
            for image_filename in image_filenames]
    with open(os.path.join(results_folder_path, 'broxmalik.bmf'), 'w') as f:
        f.write(str(len(image_filenames)) + ' 1\n')
        f.write('\n'.join(lines))

def execute_broxmalik(results_folder_path, num_images, size, command_pool=None):
    args = [BM_PATH, './broxmalik.bmf', '0', str(num_images), str(size)]
    if command_pool is None:
        p = subprocess.Popen(args, cwd=results_folder_path)
        p.wait()
    else:
        command_pool.add(executor.ExternalCommand(*args, directory=results_folder_path))

def process_images(parent_dir, results_folder_name, subsequence_folder_name, image_filenames, bm_size, command_pool=None):
    results_folder = os.path.join(parent_dir, results_folder_name)
    subsequence_folder = os.path.join(parent_dir, subsequence_folder_name)
    copy_image_files(parent_dir, subsequence_folder, image_filenames)
    copy_image_files(parent_dir, results_folder, image_filenames)
    convert_images(results_folder)
    make_bm_file(results_folder, image_filenames)
    execute_broxmalik(results_folder, len(image_filenames), bm_size, command_pool)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('name', type=str, help='name of image sequence of input images, e.g. "Log_C920_x1/3_downsampled"')
    parser.add_argument('--size', type=int, help='broxmalik step size', default=2)
    subsequences.add_subsequence_args(parser)
    args = parser.parse_args()

    command_pool = executor.concurrent.CommandPool()
    for (subsequence, start, end, subsampling) in subsequences.generate_subsequences_from_args(args):
        results_folder_name = subsequences.results_folder_name(args.size, start, args.length, subsampling)
        subsequence_folder_name = subsequences.subsequence_folder_name(start, args.length, args.subsampling)
        print results_folder_name, subsequence
        dir = os.path.join(subsequences._DATASETS_PATH, args.name)
        process_images(dir, results_folder_name, subsequence_folder_name, subsequence, args.size, command_pool)
    command_pool.run()

if __name__ == '__main__':
    main()
