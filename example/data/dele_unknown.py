import json


def adjust_factuality_labels_and_results(labels, results):
    """
    1. 去除 labels 里为 'unknown' 的项，
    2. 同步去除对应下标的 results，
    3. 返回 (new_labels, new_results)
    """
    new_labels = []
    new_results = []
    for label, result in zip(labels, results):
        if label != "unknown":  # 只保留非 'unknown'
            new_labels.append(label)
            new_results.append(result)
    return new_labels, new_results


def recalc_response_factuality(new_labels, new_results):
    """
    根据新的 claims_factuality_label / claims_factuality_result
    来计算新的 response_factuality_label / response_factuality_result。
    这里给出的规则是：只要有一个 false，就为 false，否则为 true。
    可以根据业务需求自定义逻辑。
    """
    response_label = not any(lbl == False for lbl in new_labels)
    response_result = not any(rst == False for rst in new_results)
    return response_label, response_result


def process_jsonl_file(input_path, output_path):
    unknown_items = []  # 用于记录包含 unknown 的条目 (id, prompt)

    with open(input_path, 'r', encoding='utf-8') as fin, \
            open(output_path, 'w', encoding='utf-8') as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue

            data = json.loads(line)
            old_labels = data.get("claims_factuality_label", [])
            old_results = data.get("claims_factuality_result", [])

            # 如果原始 claims_factuality_label 中包含 'unknown'，记录下来
            if any(label == "unknown" for label in old_labels):
                unknown_items.append((data.get("id"), data.get("prompt")))

            # step 1 & 2: 去除 unknown
            new_labels, new_results = adjust_factuality_labels_and_results(old_labels, old_results)

            # step 3: 根据新的 claims_factuality_* 调整 response_factuality_*
            new_response_label, new_response_result = recalc_response_factuality(new_labels, new_results)

            # 更新 data
            data["claims_factuality_label"] = new_labels
            data["claims_factuality_result"] = new_results
            data["response_factuality_label"] = new_response_label
            data["response_factuality_result"] = new_response_result

            # 写入新的文件
            fout.write(json.dumps(data, ensure_ascii=False) + "\n")

    # 所有数据处理完成后，打印包含 unknown 的条目
    if unknown_items:
        print("以下条目包含 unknown:")
        for item_id, prompt in unknown_items:
            print(f"ID: {item_id}, Prompt: {prompt}")
    else:
        print("无条目包含 unknown。")


if __name__ == "__main__":
    input_file = "output_clean0101.jsonl"
    output_file = "output_clean0101_processed.jsonl"
    process_jsonl_file(input_file, output_file)
    print(f"处理完成，输出结果保存在: {output_file}")
