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

def resequence_copy_point_clouds(source_folder, prefix, results_path, type, subsequence):
    destination_path = os.path.join(results_path, 'PointClouds', type)
    subsequences.make_dir_path(destination_path)
    for (filename, original_filename) in zip(subsequences.file_names(source_folder, prefix, '.mat'), subsequence):
        resequenced_name = prefix + os.path.splitext(original_filename)[0] + '.mat'
        shutil.copy(os.path.join(source_folder, filename), os.path.join(destination_path, resequenced_name))

def resequence_files(ms_results_folder, subsequence, results_path):
    point_clouds_folder = os.path.join(ms_results_folder, 'SuperPixels')
    resequence_copy_point_clouds(point_clouds_folder, 'points_sparse_', results_path, 'Sparse', subsequence)
    resequence_copy_point_clouds(point_clouds_folder, 'points_dense_linear_', results_path, 'DenseLinear', subsequence)
    resequence_copy_point_clouds(point_clouds_folder, 'points_dense_foreground_', results_path, 'DenseForeground', subsequence)

def main(args):
    # Copy files to results
    results_path = os.path.join(subsequences._OUTPUT_PATH, 'DepthReconstruction')
    subsequences.clear_directory(results_path)
    for (subsequence, start, end, subsampling) in subsequences.generate_subsequences_from_args(args):
        bm_results_folder_name = subsequences.results_folder_name(args.size, start, args.length, subsampling)
        dir = os.path.join(subsequences._DATASETS_PATH, args.name)
        ms_results_folder = subsequences.motseg_results_folder_path(dir, bm_results_folder_name, len(subsequence))
        resequence_files(ms_results_folder, subsequence, results_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subsequences.add_subsequence_args(parser)
    args = parser.parse_args()

    main(args)
