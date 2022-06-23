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
import re
import unicodedata

from tqdm import tqdm

from sentence_splitters import MeCabSentenceSplitter


def preprocess_text(text):
    text = unicodedata.normalize("NFKC", text)

    text = "".join(c for c in text if c.isprintable())
    text = re.sub(r"\s+", " ", text).strip()
    return text


def main(args):
    sent_splitter = MeCabSentenceSplitter(args.mecab_option)

    pageids_to_filter_out = set()
    if args.page_ids_file is not None:
        with open(args.page_ids_file) as f:
            for line in tqdm(f):
                pageid_item = json.loads(line)
                pageid = pageid_item["pageid"]

                if args.min_inlinks is not None and pageid_item["num_inlinks"] < args.min_inlinks:
                    pageids_to_filter_out.add(pageid)
                    continue

                if args.exclude_disambiguation_pages and pageid_item["is_disambiguation_page"]:
                    pageids_to_filter_out.add(pageid)
                    continue

                if args.exclude_sexual_pages and pageid_item["is_sexual_page"]:
                    pageids_to_filter_out.add(pageid)
                    continue

                if args.exclude_violent_pages and pageid_item["is_violent_page"]:
                    pageids_to_filter_out.add(pageid)
                    continue

    with gzip.open(args.paragraphs_file, "rt") as f, gzip.open(args.output_file, "wt") as fo:
        page_title = None
        is_page_processed = False
        for line in tqdm(f):
            paragraph_item = json.loads(line)
            if paragraph_item["pageid"] in pageids_to_filter_out:
                continue
            if args.html_tags_to_use is not None and paragraph_item["html_tag"] not in args.html_tags_to_use:
                continue

            if paragraph_item["title"] != page_title:
                if is_page_processed:
                    # insert a newline for separating pages
                    print("", file=fo)

                page_title = paragraph_item["title"]
                is_page_processed = False

            text = paragraph_item["text"]
            text = preprocess_text(text)
            for sentence in sent_splitter(text):
                sentence = sentence.strip()
                if len(sentence) < args.min_sentence_length:
                    continue
                if len(sentence) > args.max_sentence_length:
                    continue

                assert not "\n" in text
                assert sentence != ""
                print(sentence, file=fo)
                is_page_processed = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--paragraphs_file", type=str, required=True)
    parser.add_argument("--output_file", type=str, required=True)
    parser.add_argument("--mecab_option", type=str)
    parser.add_argument("--html_tags_to_use", nargs="+", type=str)
    parser.add_argument("--min_sentence_length", type=int, default=10)
    parser.add_argument("--max_sentence_length", type=int, default=1000)
    parser.add_argument("--page_ids_file", type=str)
    parser.add_argument("--min_inlinks", type=int)
    parser.add_argument("--exclude_disambiguation_pages", action="store_true")
    parser.add_argument("--exclude_sexual_pages", action="store_true")
    parser.add_argument("--exclude_violent_pages", action="store_true")
    args = parser.parse_args()
    main(args)
