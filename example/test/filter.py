import json

# 保留category和prompt字段
def filter_data(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            data = json.loads(line)
            filtered_data = {
                'category': data['category'],
                'prompt': data['prompt']
            }
            json.dump(filtered_data, outfile, ensure_ascii=False)
            outfile.write('\n')

if __name__ == "__main__":
    input_file = '/Users/zhangyukun/Dev/detect/factool-main/datasets/chinese/dataset_chinese.jsonl'
    output_file = 'filtered_dataset_chinese.jsonl'
    filter_data(input_file, output_file)
