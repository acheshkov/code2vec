from argparse import ArgumentParser
import os
import pandas as pd
from typing import List, Tuple, Dict, Optional
from utils import gen_emo_filename, Range, extract_lines_range_to_file


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        "-i", "--input", dest="input_csv",
        help="output name - the base name for the created dataset",
        metavar="FILE",
        required=True,
    )

    parser.add_argument(
        "-d", "--dir", dest="out_dir",
        help="output name - the base name for the created dataset",
        metavar="FILE",
        required=False,
    )
    args = parser.parse_args()

    files = pd.read_csv(args.input_csv).values.tolist()
    for filename, class_name, method_name, ranges_str in files:
        ranges = eval(ranges_str)
        for [start, end] in ranges: 
            rng = Range(start, end)
            out_fn = gen_emo_filename(os.path.basename(filename), method_name, rng)
            out_fn = os.path.join(args.out_dir, out_fn)
            extract_lines_range_to_file(filename, out_fn, rng)

