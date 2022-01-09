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

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from logzero import logger
from tqdm import tqdm


ES_SETTINGS = {
    "index": {
        "analysis": {
            "analyzer": {
                "custom_analyzer": {
                    "char_filter": [
                        "icu_normalizer"
                    ],
                    "tokenizer": "kuromoji_tokenizer",
                    "filter": [
                        "cjk_width",
                        "ja_stop",
                        "kuromoji_baseform",
                        "kuromoji_part_of_speech",
                        "kuromoji_stemmer",
                        "lowercase"
                    ]
                }
            }
        }
    }
}
ES_MAPPINGS = {
    "passage": {
        "properties": {
            "id": {"type": "integer"},
            "pageid": {"type": "integer"},
            "revid": {"type": "integer"},
            "title": {"type": "keyword"},
            "section": {"type": "keyword"},
            "text": {
                "type": "text",
                "analyzer": "custom_analyzer"
            },
            "num_inlinks": {"type": "integer"},
            "is_disambiguation_page": {"type": "boolean"},
            "is_sexual_page": {"type": "boolean"},
            "is_violent_page": {"type": "boolean"},
        }
    }
}


def main(args):
    es = Elasticsearch(hosts=[{"host": args.hostname, "port": args.port}], timeout=60)

    logger.info("Creating an Elasticsearch index")
    es.indices.create(index=args.index_name, body={"settings": ES_SETTINGS, "mappings": ES_MAPPINGS})

    logger.info("Loading page ids file")
    page_info = dict()
    with open(args.page_ids_file) as f:
        for line in tqdm(f):
            pageid_item = json.loads(line)
            pageid = pageid_item.pop("pageid")
            page_info[pageid] = pageid_item

    logger.info("Indexing documents")
    def generate_bulk_actions():
        with gzip.open(args.passages_file) as f:
            for line in tqdm(f):
                passage_item = json.loads(line)
                pageid = passage_item["pageid"]
                yield {
                    "_index": args.index_name,
                    "_type": "passage",
                    "_source": {
                        "id": passage_item["id"],
                        "pageid": passage_item["pageid"],
                        "revid": passage_item["revid"],
                        "title": passage_item["title"],
                        "section": passage_item["section"],
                        "text": passage_item["text"],
                        "num_inlinks": page_info[pageid]["num_inlinks"],
                        "is_disambiguation_page": page_info[pageid]["is_disambiguation_page"],
                        "is_sexual_page": page_info[pageid]["is_sexual_page"],
                        "is_violent_page": page_info[pageid]["is_violent_page"],
                    }
                }

    bulk(es, generate_bulk_actions())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--passages_file", type=str, required=True)
    parser.add_argument("--page_ids_file", type=str, required=True)
    parser.add_argument("--index_name", type=str, required=True)
    parser.add_argument("--hostname", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=9200)
    args = parser.parse_args()
    main(args)
