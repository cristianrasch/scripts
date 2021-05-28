#!/usr/bin/env python3

"""
Requires: imagemagick
Usage: convert.py [DIR] (defaults to ~/Pictures)
"""

from concurrent import futures
from fnmatch import fnmatch
import os
from pathlib import Path
import subprocess
import sys

SUPPORTED_FILE_EXTS = ['*.jp*g', '*.png']
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
        return True


if __name__ == '__main__':
    try:
        subprocess.run(['convert', '--version'], stdout=subprocess.DEVNULL,
                       stderr=subprocess.STDOUT)
    except (subprocess.CalledProcessError, FileNotFoundError):
        sys.exit(f'The convert cmd provided by ImageMagick is not reachable from your $PATH')


    paths = sys.argv[1:] if len(sys.argv) > 1 else ['~/Pictures']
    pics_paths = [Path(path).expanduser() for path in paths]
    if not all(path.exists() for path in pics_paths):
        sys.exit(f'Usage: {Path(__file__).name} PICS_DIR1 PICS_DIR2 PICS_DIRN')

    jobs = []
    converted = 0

    running_on_win = sys.platform == 'win32'
    exec_cls = futures.ThreadPoolExecutor if running_on_win else futures.ProcessPoolExecutor
    max_workers = None
    if running_on_win: max_workers = int(os.getenv('MAX_WORKERS', 2))

    with exec_cls(max_workers=max_workers) as executor:
        for pics_path in pics_paths:
            for dirpath, _, filenames in os.walk(pics_path):
                for filename in filenames:
                    if any(fnmatch(filename, ext) for ext in SUPPORTED_FILE_EXTS):
                        if Path(filename).stem.endswith(OPT_SUFFIX): continue

                        job = executor.submit(convert, Path(dirpath) / filename)
                        jobs.append(job)

        for job in futures.as_completed(jobs):
            if job.done() and job.result():
                converted += 1

    print(f'{converted} picture{"" if converted == 1 else "s"}.')
