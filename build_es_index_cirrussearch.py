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

import requests
from elasticsearch import Elasticsearch
from logzero import logger
from tqdm import tqdm


def main(args):
    es = Elasticsearch(hosts=[{"host": args.hostname, "port": args.port}], timeout=60)

    logger.info("Creating an Elasticsearch index")
    # https://www.elastic.co/jp/blog/loading-wikipedia
    wiki_endpoint = f"https://{args.language}.wikipedia.org/w/api.php"
    settings = requests.get(
        wiki_endpoint,
        {"action": "cirrus-settings-dump", "format": "json", "formatversion": 2}
    ).json()
    mappings = requests.get(
        wiki_endpoint,
        {"action": "cirrus-mapping-dump", "format": "json", "formatversion": 2}
    ).json()
    es.indices.create(
        index=args.index_name,
        body={
            "settings": {
                "index": {
                    "analysis": settings["content"]["page"]["index"]["analysis"],
                    "similarity": settings["content"]["page"]["index"]["similarity"],
                    "refresh_interval": -1
                }
            },
            "mappings": mappings["content"],
        },
    )

    logger.info("Indexing documents")
    assert args.bulk_size % 2 == 0, "The bulk_size should be a multiple of 2."
    with gzip.open(args.cirrus_file, "rt") as f:
        bulk_lines = []
        for line in tqdm(f):
            bulk_lines.append(line)
            if len(bulk_lines) == args.bulk_size:
                es.bulk(body="".join(bulk_lines), index=args.index_name)
                bulk_lines.clear()
        else:
            es.bulk(body="".join(bulk_lines), index=args.index_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cirrus_file", type=str, required=True)
    parser.add_argument("--index_name", type=str, required=True)
    parser.add_argument("--language", type=str, required=True)
    parser.add_argument("--hostname", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=9200)
    parser.add_argument("--bulk_size", type=int, default=200)
    args = parser.parse_args()
    main(args)
