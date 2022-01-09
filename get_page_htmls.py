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
from time import sleep
from urllib.parse import quote_plus

import grequests
import requests
from logzero import logger
from tqdm import tqdm, trange


def handle_request_exception(request, exception):
    logger.warning("Request to {} failed: {}".format(request.url, exception))


def main(args):
    if args.batch_size > 200:
        raise ValueError("batch_size is limited to be no more than 200.")

    base_url = "https://{}.wikipedia.org/api/rest_v1".format(args.language)

    # Load page ids from file
    logger.info("Loading Page IDs from file.")
    page_items = []
    with open(args.page_ids_file) as f:
        for line in tqdm(f):
            loaded_item = json.loads(line)
            title = loaded_item["title"]
            pageid = loaded_item["pageid"]
            revid = loaded_item["revid"]

            if args.mobile:
                url = "{}/page/mobile-html/{}/{}".format(base_url, quote_plus(title.replace(" ", "_")), revid)
            else:
                url = "{}/page/html/{}/{}".format(base_url, quote_plus(title.replace(" ", "_")), revid)

            page_item = {
                "title": title,
                "pageid": pageid,
                "revid": revid,
                "url": url,
            }
            page_items.append(page_item)

    headers = {"User-Agent": args.user_agent}

    # Retrieve page htmls
    logger.info("Retrieving Page HTMLs")
    failed_pages = []
    with gzip.open(args.output_file, "wt") as fo:
        for i in trange(0, len(page_items), args.batch_size):
            batch_page_items = page_items[i:i + args.batch_size]

            reqs = (
                grequests.get(page_item["url"], headers=headers, timeout=args.timeout)
                for page_item in batch_page_items
            )
            responses = grequests.map(reqs, exception_handler=handle_request_exception)
            assert len(responses) == len(batch_page_items)

            for page_item, response in zip(batch_page_items, responses):
                if response is not None:
                    page_item["html"] = response.text
                    print(json.dumps(page_item, ensure_ascii=False), file=fo)
                else:
                    logger.warning(
                        "Request for the page %s (pageid=%s, revid=%s) failed. The request will be tried again later.",
                        page_item["title"], page_item["pageid"], page_item["revid"],
                    )
                    failed_pages.append(page_item)

            # Requests should be limited to 200 requests/sec.
            # See https://www.mediawiki.org/wiki/REST_API.
            sleep(args.batch_size / 200)

        # Retry failed requests
        if len(failed_pages) > 0:
            logger.info("Retrying failed %s requests", len(failed_pages))
            for page_item in failed_pages:
                try:
                    response = requests.get(page_item["url"], headers=headers, timeout=args.timeout * 5)
                    response.raise_for_status()
                except Exception as e:
                    logger.warning("Request for %s failed: %s", url, e)
                    continue

                page_item["html"] = response.text
                print(json.dumps(page_item, ensure_ascii=False), file=fo)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--page_ids_file", type=str, required=True)
    parser.add_argument("--output_file", type=str, required=True)
    parser.add_argument("--language", type=str, required=True)
    parser.add_argument("--user_agent", type=str, required=True)
    parser.add_argument("--batch_size", type=int, default=20)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--mobile", action="store_true")
    args = parser.parse_args()
    main(args)
