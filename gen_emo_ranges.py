import time
import multiprocessing as mp
from argparse import ArgumentParser
import re
import os
import random
import subprocess
import sys
import pandas as pd
import pickle
import tempfile
from typing import List, Tuple, Dict, Optional
from enum import Enum, auto
from utils import extract_method, get_source_code, Range, complement_range
from find_emos import find_emos, count_all_class_declarations



def get_method_loc(filename: str, method_name: str, method_start_line: int) -> int:
  source_code = get_source_code(filename)
  method_code = extract_method(source_code, method_name, method_start_line)
  return len(method_code.split('\n'))


def process_single_file(filename, class_name, method_name, method_start_line, ins_start, ins_end, method_loc_limit=50):

  def _complement(filename: str, range: Range) -> Range:
    sc = get_source_code(filename)
    return complement_range(sc,  Range(range.start, range.end))

  try:
    # if count_all_class_declarations(filename) > 1:
    #   print('File must contain only one class', filename, class_name, method_name, method_start_line, ins_start, ins_end)
    #   return None
    loc = get_method_loc(filename, method_name, method_start_line)
    if loc >= method_loc_limit: 
      return None
    if not (ins_start > method_start_line and  ins_end < method_start_line + loc):
      print('Insertion out of range method declaration', filename, class_name, method_name, method_start_line, ins_start, ins_end)
      return None
    #print(filename)
    ranges = find_emos(filename, class_name, method_name, method_start_line)
    ranges = [_complement(filename, r) for r in ranges]
    ranges = list(filter(lambda v: v.end - v.start > 1, ranges))
    
    return filename, class_name, method_name, str(ranges)
  except:
    # print("Unexpected error:", sys.exc_info()[0])
    return None



if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        "-i", "--input", dest="input_csv",
        help="output name - the base name for the created dataset",
        metavar="FILE",
        required=True,
    )
    parser.add_argument(
        "-o", "--o", dest="output_csv",
        help="output name - the base name for the created dataset",
        metavar="FILE",
        required=True,
    )

    parser.add_argument(
        "-d", "--dir", dest="dir",
        help="output name - the base name for the created dataset",
        metavar="FILE",
        required=False,
    )
    parser.add_argument("-threads", "--num_threads", dest="num_threads", required=False, default=1, type=int)
    parser.add_argument("-method_loc_limit", "--method_loc_limit", dest="method_loc_limit", required=False, default=300, type=int)
    
    parser.add_argument("-chunks", "--chunks", dest="chunks", required=False, default=1000, type=int)
    parser.add_argument("-n", "--n", dest="n", required=False, default=10)

    def chunks(lst, n):
      """Yield successive n-sized chunks from lst."""
      for i in range(0, len(lst), n):
          yield lst[i: i + n]

    
    args = parser.parse_args()
    start = time.time()
    columns_to_use = [
      'output_filename', 'project_name', 
      'class_name', 'method_where_invocation_occurred', 
      'start_line_of_function_where_invocation_occurred', 'can_be_parsed',
      'inline_insertion_line_start', 'inline_insertion_line_end'
    ]
    files = pd.read_csv(args.input_csv)
    files = files[files.can_be_parsed == True]
    files.start_line_of_function_where_invocation_occurred = files.start_line_of_function_where_invocation_occurred.astype(int)
    files = files[columns_to_use][[
      'output_filename', 'class_name', 'method_where_invocation_occurred', 
      'start_line_of_function_where_invocation_occurred',
      'inline_insertion_line_start', 'inline_insertion_line_end'
    ]].values.tolist()
    files = list(map(tuple, files))
    
    if args.dir is not None:
      files = list(map(lambda ts: (os.path.join(args.dir, ts[0]), ) + ts[1: ], files))
    if args.method_loc_limit is not None:
      files = list(map(lambda ts: ts + (args.method_loc_limit, ), files))
    
    data = []
    #pool = mp.Pool(args.num_threads, maxtasksperchild=100)
    
    for ch in chunks(files, args.chunks):
      data = []
      pool = mp.Pool(args.num_threads)
      print(list(map(lambda v: os.path.basename(v[0]), ch)))
      data = pool.starmap(process_single_file, ch)
      data = list(filter(lambda v: v is not None, data))
      pd.DataFrame(
        data, 
        columns=['file_name', 'class_name', 'method_name', 'ranges']
      ).to_csv(args.output_csv, header=False, mode='a', index=False)
      pool.close()
      pool.join()