import json


def process_data(data):
    # 新的结构，按照要求初始化
    processed_data = {
        "prompt": data.get("prompt"),
        "response": data.get("response"),
        "response_factuality": data.get("response_factuality"),
        "claims": [],
        "evidence": [],
        "claims_factuality_label": []
    }

    # 处理句子级数据
    for sentence_key, sentence_data in data.get("sentences", {}).items():
        # 获取每个句子的所有claim
        claims = sentence_data.get("claims", [])
        factuality_labels = sentence_data.get("claims_factuality_label", [])
        for index, claim in enumerate(claims):
            # 合并人类和自动证据
            human_evidence = sentence_data.get("human_evidence", [])
            auto_evidence = sentence_data.get("auto_evidence", [])
            combined_evidence = human_evidence + [item for sublist in auto_evidence for item in sublist]

            # 获取对应claim的事实标签，确保一一对应，若超出范围则按默认值处理（这里可根据实际需求调整默认值逻辑）
            if index < len(factuality_labels):
                claim_factuality_label = factuality_labels[index]
            else:
                claim_factuality_label = False  # 可按需修改默认值，比如设为None等

            # 将句子的声明、证据和事实标签添加到声明级数据结构
            processed_data["claims"].append(claim)
            processed_data["evidence"].append(combined_evidence)
            processed_data["claims_factuality_label"].append(claim_factuality_label)

    return processed_data


def process_jsonl(input_file, output_file, max_lines=None):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        line_count = 0
        for line in infile:
            if max_lines and line_count >= max_lines:
                break

            data = json.loads(line)  # 读取一行数据并解析为字典
            processed = process_data(data)  # 处理数据
            print(json.dumps(processed, indent=2))
            json.dump(processed, outfile, ensure_ascii=False, separators=(',', ':'))  # 写入处理后的数据
            outfile.write("\n")  # 换行

            line_count += 1
        print(f"Processed {line_count} lines.")


def main():
    # 调用函数，设置最大行数（例如读取前10行）
    # process_jsonl('input.jsonl', 'output1227.jsonl', max_lines=2)
    process_jsonl('factcheck-GPT-benchmark.jsonl', 'output1227gpt.jsonl', max_lines=94)


if __name__ == "__main__":
    main()