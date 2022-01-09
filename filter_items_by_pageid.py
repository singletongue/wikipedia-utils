# Copyright 2022 Masatoshi Suzuki (@singletongue)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import argparse
import gzip
import json

from logzero import logger
from tqdm import tqdm


def main(args):
    logger.info("Loading Page IDs from file.")
    page_ids = set(json.loads(line)["pageid"] for line in tqdm(open(args.pageids_file)))
    logger.info("Loaded %d Page IDs.", len(page_ids))

    logger.info("Filtering input file by the Page IDs.")
    n_skipped = 0
    with gzip.open(args.input_file, "rt") if args.input_file.endswith(".gz") else open(args.input_file) as f, \
         gzip.open(args.output_file, "wt") if args.output_file.endswith(".gz") else open(args.output_file, "w") as fo:
        for line in tqdm(f):
            item = json.loads(line)
            if item["pageid"] not in page_ids:
                n_skipped += 1
                continue

            print(line.rstrip("\n"), file=fo)

    logger.info("Finished processing input file.")
    logger.info("%d items have been skipped.", n_skipped)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str, required=True)
    parser.add_argument("--pageids_file", type=str, required=True)
    parser.add_argument("--output_file", type=str, required=True)
    args = parser.parse_args()
    main(args)
