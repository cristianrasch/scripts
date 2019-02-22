#!/usr/bin/env python3

"""
Requires: imagemagick
Usage: convert.py [DIR] (defaults to ~/Pictures)
"""

from concurrent import futures
import fnmatch
import os
from pathlib import Path
import subprocess
import sys

OPT_SUFFIX = '_opt'

def convert(img_path):
    src_path = str(img_path)
    dest_path = str(img_path.with_name(img_path.stem + OPT_SUFFIX +
                                       img_path.suffix))

    try:
        subprocess.run(['convert', src_path, '-auto-orient',
                        '-quality', '85', '-thumbnail', "1920x1080>",
                        '-sharpen', "0x1.0", dest_path],
                       check=True, text=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as err:
        print('%s could not be converted: %s (err co: %d)' %
              (src_path, err.stderr, err.returncode))
    else:
        img_path.unlink()

pic_path = Path(sys.argv[1] if len(sys.argv) > 1 else '~/Pictures').expanduser()
jobs = []

converted = 0
def job_done_cb(_):
    global converted
    converted += 1

with futures.ProcessPoolExecutor() as executor:
    for dirpath, _, filenames in os.walk(pic_path):
        for filename in filenames:
            if fnmatch.fnmatch(filename, '*.jp*g'):
                if Path(filename).stem.endswith(OPT_SUFFIX): continue

                job = executor.submit(convert, Path(dirpath) / filename)
                job.add_done_callback(job_done_cb)
                jobs.append(job)

print(converted, 'images converted.')
