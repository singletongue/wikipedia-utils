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
import os


class MeCabSentenceSplitter(object):
    def __init__(self, mecab_option=None):
        import fugashi
        if mecab_option is None:
            import unidic_lite
            dic_dir = unidic_lite.DICDIR
            mecabrc = os.path.join(dic_dir, "mecabrc")
            mecab_option = "-d {} -r {}".format(dic_dir, mecabrc)

        self.mecab = fugashi.GenericTagger(mecab_option)

    def __call__(self, text):
        sentences = []
        start = 0
        end = 0
        for line in self.mecab.parse(text).split("\n"):
            if line == "EOS":
                if len(text[start:]) > 0:
                    sentences.append(text[start:])
                break

            token, token_info = line.split("\t", maxsplit=1)
            end = text.index(token, end) + len(token)
            if "記号" in token_info and "句点" in token_info:
                sentences.append(text[start:end])
                start = end

        return sentences
