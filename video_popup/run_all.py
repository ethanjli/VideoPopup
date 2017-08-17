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
import run_broxmalik
import run_matlab_input
import run_motseg
import run_matlab_motseg
import run_depth

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subsequences.add_subsequence_args(parser)
    args = parser.parse_args()

    run_broxmalik.main(args)
    run_matlab_input.main(args)
    run_motseg.main(args)
    run_matlab_motseg.main(args)
    run_depth.main(args)
