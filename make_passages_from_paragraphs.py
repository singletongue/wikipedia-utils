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
from typing import Callable, Optional

from tqdm import tqdm

from sentence_splitters import MeCabSentenceSplitter


def generate_passages(
    paragraphs_file: str,
    passage_unit: str,
    passage_boundary: str,
    append_title_to_passage_text: bool,
    max_passage_length: int,
    as_long_as_possible: bool,
    sentence_splitter: Optional[Callable] = None
):
    assert passage_unit in ("section", "paragraph", "sentence")
    assert passage_boundary in ("title", "section", "paragraph")

    passage_id = 0
    last_pageid = None
    last_revid = None
    last_title = None
    last_section = None
    section_text = ""
    unit_texts = []

    def generate_passage_texts(unit_texts):
        if as_long_as_possible:
            buffer_text = ""
            for unit_text in unit_texts:
                assert len(unit_text) <= max_passage_length
                if len(buffer_text) + len(unit_text) > max_passage_length:
                    yield buffer_text
                    buffer_text = ""

                buffer_text += unit_text
            else:
                if len(buffer_text) > 0:
                    yield buffer_text
        else:
            for unit_text in unit_texts:
                assert len(unit_text) <= max_passage_length
                yield unit_text

    with gzip.open(paragraphs_file, "rt") as f:
        for line in f:
            paragraph_item = json.loads(line)
            pageid = paragraph_item["pageid"]
            revid = paragraph_item["revid"]
            title = paragraph_item["title"]
            section = paragraph_item["section"]
            paragraph_text = paragraph_item["text"]

            if (title != last_title) or \
               (passage_boundary == "paragraph") or \
               (passage_boundary == "section" and section != last_section):
                for passage_text in generate_passage_texts(unit_texts):
                    passage_id += 1
                    if append_title_to_passage_text:
                        passage_text = last_title + args.title_passage_boundary + passage_text

                    assert last_pageid is not None
                    assert last_revid is not None
                    assert last_title is not None
                    assert last_section is not None
                    output_item = {
                        "id": passage_id,
                        "pageid": last_pageid,
                        "revid": last_revid,
                        "title": last_title,
                        "section": last_section,
                        "text": passage_text,
                    }
                    yield output_item

                unit_texts = []

            if passage_unit == "section":
                if section != last_section and len(section_text) > 0:
                    if len(section_text) <= max_passage_length:
                        unit_texts.append(section_text)

                    section_text = ""

                section_text += paragraph_text
            elif passage_unit == "paragraph":
                if len(paragraph_text) <= max_passage_length:
                    unit_texts.append(paragraph_text)
            elif passage_unit == "sentence":
                unit_texts += [sent for sent in sentence_splitter(paragraph_text) if len(sent) <= max_passage_length]

            last_pageid = pageid
            last_revid = revid
            last_title = title
            last_section = section
        else:
            for passage_text in generate_passage_texts(unit_texts):
                passage_id += 1
                if append_title_to_passage_text:
                    passage_text = last_title + passage_text

                assert last_pageid is not None
                assert last_revid is not None
                assert last_title is not None
                assert last_section is not None
                output_item = {
                    "id": passage_id,
                    "pageid": last_pageid,
                    "revid": last_revid,
                    "title": last_title,
                    "section": last_section,
                    "text": passage_text,
                }
                yield output_item


def main(args: argparse.Namespace):
    sentence_splitter = MeCabSentenceSplitter(args.mecab_option)

    with gzip.open(args.output_file, "wt") as fo:
        passage_generator = generate_passages(
            paragraphs_file=args.paragraphs_file,
            passage_unit=args.passage_unit,
            passage_boundary=args.passage_boundary,
            append_title_to_passage_text=args.append_title_to_passage_text,
            max_passage_length=args.max_passage_length,
            as_long_as_possible=args.as_long_as_possible,
            sentence_splitter=sentence_splitter
        )
        for passage_item in tqdm(passage_generator):
            print(json.dumps(passage_item, ensure_ascii=False), file=fo)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--paragraphs_file", type=str, required=True)
    parser.add_argument("--output_file", type=str, required=True)
    parser.add_argument("--passage_unit", type=str, default="paragraph")
    parser.add_argument("--passage_boundary", type=str, required="section")
    parser.add_argument("--append_title_to_passage_text", action="store_true")
    parser.add_argument("--title_passage_boundary", type=str, default=" ")
    parser.add_argument("--max_passage_length", type=int, default=1000,
        help="It does not take page title lengths into account even if the "
             "--append_title_to_passage_text option is enabled")
    parser.add_argument("--as_long_as_possible", action="store_true")
    parser.add_argument("--mecab_option", type=str)
    args = parser.parse_args()
    main(args)
