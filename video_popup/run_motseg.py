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

def execute_motseg(subsequence_folder_path, bm_results_folder_path, num_images, command_pool=None):
    tracks_path = os.path.join(bm_results_folder_path, 'broxmalikTracks{}.dat'.format(num_images))
    args = ['python', '-m', 'video_popup.motion_segmentation.video_popup_motseg', '--images_dir', subsequence_folder_path, '--tracks_path', tracks_path, '--endframe', str(num_images)]
    if command_pool is None:
        p = subprocess.Popen(args, cwd=subsequences._ROOT_PATH)
        p.wait()
    else:
        command_pool.add(executor.ExternalCommand(*args, directory=subsequences._ROOT_PATH))

def process_tracks(parent_dir, bm_results_folder_name, subsequence_folder_name, image_filenames, command_pool=None):
    bm_results_folder = subsequences.bm_results_folder_path(parent_dir, bm_results_folder_name)
    subsequence_folder = os.path.join(parent_dir, subsequence_folder_name)
    execute_motseg(subsequence_folder, bm_results_folder, len(image_filenames), command_pool)

def copy_files(ms_results_folder, results_path):
    subsequences.clear_directory(results_path)
    print os.path.join(ms_results_folder, 'results.mat')
    shutil.copy(os.path.join(ms_results_folder, 'results.mat'),
                os.path.join(results_path, 'results.mat'))

def main():
    parser = argparse.ArgumentParser()
    subsequences.add_subsequence_args(parser)
    args = parser.parse_args()

    # Run motion segmentation
    command_pool = executor.concurrent.CommandPool()
    for (subsequence, start, end, subsampling) in subsequences.generate_subsequences_from_args(args):
        bm_results_folder_name = subsequences.results_folder_name(args.size, start, args.length, subsampling)
        subsequence_folder_name = subsequences.subsequence_folder_name(start, args.length, subsampling)
        print bm_results_folder_name
        dir = os.path.join(subsequences._DATASETS_PATH, args.name)
        process_tracks(dir, bm_results_folder_name, subsequence_folder_name, subsequence, command_pool)
    command_pool.run()

    # Copy files to results
    for (subsequence, start, end, subsampling) in subsequences.generate_subsequences_from_args(args):
        bm_results_folder_name = subsequences.results_folder_name(args.size, start, args.length, subsampling)
        dir = os.path.join(subsequences._DATASETS_PATH, args.name)
        ms_results_folder = subsequences.motseg_results_folder_path(dir, bm_results_folder_name, len(subsequence))
        results_path = os.path.join(subsequences._OUTPUT_PATH, str(start), 'MotionSegmentation')
        copy_files(ms_results_folder, results_path)

if __name__ == '__main__':
    main()
