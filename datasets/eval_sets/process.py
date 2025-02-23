import json


def process_data(input_file, output_file):
    """
    处理输入数据集，生成新的数据集格式，输出到指定文件
    """
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            data = json.loads(line)

            # 合并claims和相应的claims_factuality_label
            claims = []
            claims_factuality_labels = []
            for sentence_key in data['sentences']:
                sentence = data['sentences'][sentence_key]
                claims.extend(sentence['claims'])
                claims_factuality_labels.extend([sentence['sentence_factuality_label']] * len(sentence['claims']))

            # 合并evidence
            evidence = []
            for sentence_key in data['sentences']:
                sentence = data['sentences'][sentence_key]
                evidence.extend(sentence['human_evidence'])
                evidence.extend(sentence['auto_evidence'])

            # 生成新结构的数据
            revised_data = {
                "prompt": data["prompt"],
                "response": data["response"],
                "revised_response": data["revised_response"],
                "response_factuality": data["response_factuality"],
                "claims": claims,
                "claims_factuality_label": claims_factuality_labels,
                "evidence": evidence
            }

            # 写入新数据到输出文件
            outfile.write(json.dumps(revised_data, ensure_ascii=False) + '\n')


# 使用if __name__ == '__main__'来执行脚本
if __name__ == '__main__':
    input_file = 'input.jsonl'  # 这里替换为你的输入文件路径
    output_file = 'output.jsonl'  # 这里替换为你的输出文件路径
    process_data(input_file, output_file)
