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


def filter_text(text):
    # filter out text containing equations
    if "\displaystyle" in text:
        return False

    return True


def preprocess_text(text, title=None):
    text = unicodedata.normalize("NFKC", text)

    # remove invisible characters
    text = "".join(c for c in text if c.isprintable())

    # remove templates
    text = re.sub(r"\[\d+?\]", "", text)
    text = re.sub(r"\[要.+?\]", "", text)
    text = re.sub(r"\{\{+[^{}]+?\}\}+", "", text)

    # remove navigation
    if title is not None:
        text = re.sub(r"^.+? \> " + re.escape(title), "", text)

    # remove footnotes
    text = re.sub(r" \^ .+", "", text)
    # remove annotations
    text = re.sub(r"\[(要出典|リンク切れ|.+?\?)\]", "", text)

    text = re.sub(r"\s+", " ", text).strip()
    return text


def main(args):
    sent_splitter = MeCabSentenceSplitter(args.mecab_option)

    with gzip.open(args.cirrus_file, "rt") as f, gzip.open(args.output_file, "wt") as fo:
        for line in tqdm(f):
            item = json.loads(line)
            if "index" in item:
                page_id = item["index"]["_id"]
            else:
                assert page_id is not None

                title = item["title"]
                text = item["text"]
                templates = item["template"]
                num_inlinks = item.get("incoming_links", 0)

                if args.min_inlinks is not None and num_inlinks < args.min_inlinks:
                    continue
                if args.exclude_disambiguation_pages and "Template:Dmbox" in templates:
                    continue
                if args.exclude_sexual_pages and "Template:性的" in templates:
                    continue
                if args.exclude_violent_pages and "Template:暴力的" in templates:
                    continue

                text = preprocess_text(text, title=title)

                is_processed = False
                for sentence in sent_splitter(text):
                    sentence = sentence.strip()
                    if len(sentence) < args.min_sentence_length:
                        continue
                    if len(sentence) > args.max_sentence_length:
                        continue
                    if not filter_text(sentence):
                        continue

                    assert not "\n" in text
                    assert sentence != ""
                    print(sentence, file=fo)
                    is_processed = True

                if is_processed:
                    # insert a newline for separating pages
                    print("", file=fo)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cirrus_file", type=str, required=True)
    parser.add_argument("--output_file", type=str, required=True)
    parser.add_argument("--mecab_option", type=str)
    parser.add_argument("--min_sentence_length", type=int, default=20)
    parser.add_argument("--max_sentence_length", type=int, default=1000)
    parser.add_argument("--min_inlinks", type=int)
    parser.add_argument("--exclude_disambiguation_pages", action="store_true")
    parser.add_argument("--exclude_sexual_pages", action="store_true")
    parser.add_argument("--exclude_violent_pages", action="store_true")
    args = parser.parse_args()
    main(args)
