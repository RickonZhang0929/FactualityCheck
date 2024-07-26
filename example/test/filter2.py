import json


def extract_prompts(input_file, output_file):
    prompts = []
    with open(input_file, 'r', encoding='utf-8') as infile:
        for line in infile:
            data = json.loads(line)
            prompts.append(data['prompt'])

    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(prompts, outfile, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    input_file = '/Users/zhangyukun/Dev/detect/factool-main/datasets/chinese/dataset_chinese.jsonl'
    output_file = 'prompts_list.json'
    extract_prompts(input_file, output_file)
