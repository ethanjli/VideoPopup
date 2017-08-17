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

def execute_depth(ms_results_folder_path, num_images, command_pool=None):
    results_path = os.path.join(ms_results_folder_path, 'results.pkl')
    args = ['python', '-m', 'video_popup.depth_reconstruction.depth_reconstruction_test', '--seg_file', results_path, '--endframe', str(num_images)]
    if command_pool is None:
        p = subprocess.Popen(args, cwd=subsequences._ROOT_PATH)
        p.wait()
    else:
        command_pool.add(executor.ExternalCommand(*args, directory=subsequences._ROOT_PATH))

def process_segments(parent_dir, bm_results_folder_name, image_filenames, command_pool=None):
    ms_results_folder = subsequences.motseg_results_folder_path(parent_dir, bm_results_folder_name, len(image_filenames))
    execute_depth(ms_results_folder, len(image_filenames), command_pool)

def copy_point_clouds(source_folder, prefix, results_path, type):
    subsequences.copy_files(source_folder, prefix, '.mat', os.path.join(results_path, 'PointClouds', type))

def copy_files(ms_results_folder, results_path):
    subsequences.clear_directory(results_path)
    shutil.copy(os.path.join(ms_results_folder, 'SparseResults', 'results.mat'),
                os.path.join(results_path, 'sparse_results.mat'))
    point_clouds_folder = os.path.join(ms_results_folder, 'SuperPixels')
    copy_point_clouds(point_clouds_folder, 'points_sparse_', results_path, 'Sparse')
    copy_point_clouds(point_clouds_folder, 'points_dense_linear_', results_path, 'DenseLinear')
    copy_point_clouds(point_clouds_folder, 'points_dense_foreground_', results_path, 'DenseForeground')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('name', type=str, help='name of image sequence of input images, e.g. "Log_C920_x1/3_downsampled"')
    parser.add_argument('--size', type=int, help='broxmalik step size', default=2)
    subsequences.add_subsequence_args(parser)
    args = parser.parse_args()

    # Run depth reconstruction
    command_pool = executor.concurrent.CommandPool()
    for (subsequence, start, end, subsampling) in subsequences.generate_subsequences_from_args(args):
        bm_results_folder_name = subsequences.results_folder_name(args.size, start, args.length, subsampling)
        print bm_results_folder_name
        dir = os.path.join(subsequences._DATASETS_PATH, args.name)
        process_segments(dir, bm_results_folder_name, subsequence, command_pool)
    command_pool.run()

    # Copy files to results
    for (subsequence, start, end, subsampling) in subsequences.generate_subsequences_from_args(args):
        bm_results_folder_name = subsequences.results_folder_name(args.size, start, args.length, subsampling)
        dir = os.path.join(subsequences._DATASETS_PATH, args.name)
        ms_results_folder = subsequences.motseg_results_folder_path(dir, bm_results_folder_name, len(subsequence))
        results_path = os.path.join(subsequences._OUTPUT_PATH, str(start), 'DepthReconstruction')
        copy_files(ms_results_folder, results_path)

if __name__ == '__main__':
    main()
