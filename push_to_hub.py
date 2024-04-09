import argparse

from datasets import Features, Value, load_dataset


DEFAULT_DATASET_REPO_ID = "singletongue/wikipedia-utils"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset_file", type=str, required=True)
    parser.add_argument("--config_name", type=str, required=True)
    parser.add_argument("--dataset_repo_id", type=str, default=DEFAULT_DATASET_REPO_ID)
    args = parser.parse_args()

    if args.config_name.startswith("corpus"):
        dataset_type = "text"
        features = Features({"text": Value("string")})
    elif args.config_name.startswith("paragraphs"):
        dataset_type = "json"
        features = Features(
            {
                "id": Value("string"),
                "pageid": Value("int64"),
                "revid": Value("int64"),
                "paragraph_index": Value("int64"),
                "title": Value("string"),
                "section": Value("string"),
                "text": Value("string"),
                "html_tag": Value("string"),
            }
        )
    elif args.config_name.startswith("passages"):
        dataset_type = "json"
        features = Features(
            {
                "id": Value("int64"),
                "pageid": Value("int64"),
                "revid": Value("int64"),
                "title": Value("string"),
                "section": Value("string"),
                "text": Value("string"),
            }
        )
    else:
        raise ValueError("Invalid dataset config name is specified.")

    print("loading the dataset")
    dataset = load_dataset(dataset_type, data_files={"train": str(args.dataset_file)}, features=features)

    print(f"pushing the dataset to {args.dataset_repo_id} with config name {args.config_name}")
    dataset.push_to_hub(args.dataset_repo_id, config_name=args.config_name)

if __name__ == "__main__":
    main()
