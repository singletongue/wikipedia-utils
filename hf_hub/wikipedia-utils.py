# Copyright 2020 The HuggingFace Datasets Authors and the current dataset script contributor.
# Copyright 2023 Masatoshi Suzuki (@singletongue)
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
"""Wikipedia-Utils: Preprocessed Wikipedia Texts for NLP"""

import io
from typing import Iterator, List, Tuple

import datasets
import pyarrow as pa


_DESCRIPTION = "Preprocessed Wikipedia texts generated with scripts in singletongue/wikipedia-utils repo."

_HOMEPAGE = "https://github.com/singletongue/wikipedia-utils"

_LICENSE = "The content of Wikipedia is licensed under the CC-BY-SA 3.0 and GFDL licenses."

_URL_BASE = "https://github.com/singletongue/wikipedia-utils/releases/download"
_URLS = {
    "corpus-jawiki-20230403": f"{_URL_BASE}/2023-04-03/corpus-jawiki-20230403.txt.gz",
    "corpus-jawiki-20230403-cirrus": f"{_URL_BASE}/2023-04-03/corpus-jawiki-20230403-cirrus.txt.gz",
    "corpus-jawiki-20230403-filtered-large": f"{_URL_BASE}/2023-04-03/corpus-jawiki-20230403-filtered-large.txt.gz",
    "paragraphs-jawiki-20230403": f"{_URL_BASE}/2023-04-03/paragraphs-jawiki-20230403.json.gz",
    "passages-c300-jawiki-20230403": f"{_URL_BASE}/2023-04-03/passages-c300-jawiki-20230403.json.gz",
    "passages-c400-jawiki-20230403": f"{_URL_BASE}/2023-04-03/passages-c400-jawiki-20230403.json.gz",
    "passages-para-jawiki-20230403": f"{_URL_BASE}/2023-04-03/passages-para-jawiki-20230403.json.gz",
}

_VERSION = datasets.Version("1.0.0")


class WikipediaUtils(datasets.ArrowBasedBuilder):
    """Wikipedia-Utils dataset."""

    BUILDER_CONFIGS = [datasets.BuilderConfig(name=name, version=_VERSION) for name in _URLS.keys()]

    def _info(self) -> datasets.DatasetInfo:
        if self.config.name.startswith("corpus"):
            features = datasets.Features({"text": datasets.Value("string")})
        elif self.config.name.startswith("paragraphs"):
            features = datasets.Features(
                {
                    "id": datasets.Value("string"),
                    "pageid": datasets.Value("int64"),
                    "revid": datasets.Value("int64"),
                    "paragraph_index": datasets.Value("int64"),
                    "title": datasets.Value("string"),
                    "section": datasets.Value("string"),
                    "text": datasets.Value("string"),
                    "html_tag": datasets.Value("string"),
                }
            )
        elif self.config.name.startswith("passages"):
            features = datasets.Features(
                {
                    "id": datasets.Value("int64"),
                    "pageid": datasets.Value("int64"),
                    "revid": datasets.Value("int64"),
                    "title": datasets.Value("string"),
                    "section": datasets.Value("string"),
                    "text": datasets.Value("string"),
                }
            )
        else:
            raise ValueError("Invalid dataset config name is specified.")

        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=features,
            homepage=_HOMEPAGE,
            license=_LICENSE,
        )

    def _split_generators(self, dl_manager: datasets.DownloadManager) -> List[datasets.SplitGenerator]:
        url = _URLS[self.config.name]
        filepath = dl_manager.download_and_extract(url)
        return [datasets.SplitGenerator(name=datasets.Split.TRAIN, gen_kwargs={"filepath": filepath})]

    def _generate_tables(self, filepath: str, chunksize: int = 10 << 20) -> Iterator[Tuple[int, pa.Table]]:
        if self.config.name.startswith("corpus"):
            with open(filepath) as f:
                batch_idx = 0
                while True:
                    batch = f.read(chunksize)
                    if not batch:
                        break

                    batch += f.readline()
                    batch = [line.rstrip("\n") for line in io.StringIO(batch).readlines()]
                    pa_table = pa.Table.from_arrays([pa.array(batch)], names=["text"])

                    yield batch_idx, pa_table
                    batch_idx += 1
        elif self.config.name.startswith(("paragraphs", "passages")):
            with open(filepath, "rb") as f:
                batch_idx = 0
                block_size = max(chunksize // 32, 16 << 10)
                while True:
                    batch = f.read(chunksize)
                    if not batch:
                        break

                    batch += f.readline()
                    pa_table = pa.json.read_json(
                        io.BytesIO(batch), read_options=pa.json.ReadOptions(block_size=block_size)
                    )

                    yield batch_idx, pa_table
                    batch_idx += 1
        else:
            raise ValueError("Invalid dataset config name is specified.")
