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

from tqdm import tqdm


def main(args):
    with gzip.open(args.cirrus_file, "rt") as f, open(args.output_file, "w") as fo:
        title = None
        pageid = None
        revid = None
        for line in tqdm(f):
            item = json.loads(line)
            if "index" in item:
                pageid = int(item["index"]["_id"])
            else:
                assert pageid is not None

                title = item["title"]
                revid = item["version"]
                num_inlinks = item.get("incoming_links", 0)

                templates = item["template"]
                is_disambiguation_page = "Template:Dmbox" in templates
                is_sexual_page = "Template:性的" in templates
                is_violent_page = "Template:暴力的" in templates

                output_item = {
                    "title": title,
                    "pageid": pageid,
                    "revid": revid,
                    "num_inlinks": num_inlinks,
                    "is_disambiguation_page": is_disambiguation_page,
                    "is_sexual_page": is_sexual_page,
                    "is_violent_page": is_violent_page,
                }
                print(json.dumps(output_item, ensure_ascii=False), file=fo)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cirrus_file", type=str, required=True)
    parser.add_argument("--output_file", type=str, required=True)
    args = parser.parse_args()
    main(args)
