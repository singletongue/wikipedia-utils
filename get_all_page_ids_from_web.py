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
import json

import requests
from tqdm import tqdm


def main(args):
    base_url = f"https://{args.language}.wikipedia.org/w/api.php"

    page_request_params = {
        "action": "query",
        "prop": "revisions",
        "generator": "allpages",
        "gapfilterredir": "nonredirects",
        "gaplimit": args.gaplimit,
        "format": "json",
        "formatversion": 2,
    }

    with open(args.output_file, "w") as fo, tqdm(unit="pages") as pbar:
        while True:
            page_response = requests.get(base_url, page_request_params).json()
            if "query" in page_response:
                for page_item in page_response["query"]["pages"]:
                    output_item = {
                        "title": page_item["title"],
                        "pageid": page_item["pageid"],
                        "revid": page_item["revisions"][0]["revid"]
                    }

                    print(json.dumps(output_item, ensure_ascii=False), file=fo)
                    pbar.update(1)

            if "continue" in page_response:
                page_request_params.update(page_response["continue"])
            else:
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", type=str, required=True)
    parser.add_argument("--output_file", type=str, required=True)
    parser.add_argument("--gaplimit", type=int, default=20)
    args = parser.parse_args()
    main(args)
