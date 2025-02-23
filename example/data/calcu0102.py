import json
import copy


def analyze_output_file_to_jsonl(input_file, output_file):
    # --- 1) 初始化统计容器 ---
    # 段落级别计数
    paragraph_stats = {
        "correct_correct": 0,  # (label=True,  result=True)
        "correct_wrong": 0,  # (label=True,  result=False)
        "error_correct": 0,  # (label=False, result=False)
        "error_wrong": 0,  # (label=False, result=True)
        "total": 0
    }
    # 声明级别计数
    claims_stats = {
        "correct_correct": 0,
        "correct_wrong": 0,
        "error_correct": 0,
        "error_wrong": 0,
        "total": 0
    }

    # 用于存放「段落级别」出现错误的条目（即 correct_wrong 或 error_wrong）
    paragraph_error_items = {
        "correct_wrong": [],
        "error_wrong": []
    }

    # --- 2) 读取并统计 ---
    with open(input_file, 'r', encoding='utf-8') as fin:
        for line in fin:
            line = line.strip()
            if not line:
                continue

            data = json.loads(line)

            # ===== 段落级别 =====
            response_label = data.get("response_factuality_label")
            response_result = data.get("response_factuality_result")
            if isinstance(response_label, bool) and isinstance(response_result, bool):
                paragraph_stats["total"] += 1
                if response_label and response_result:
                    paragraph_stats["correct_correct"] += 1
                elif response_label and not response_result:
                    paragraph_stats["correct_wrong"] += 1
                    # 记录整条数据到错误条目中
                    paragraph_error_items["correct_wrong"].append(copy.deepcopy(data))
                elif not response_label and not response_result:
                    paragraph_stats["error_correct"] += 1
                elif not response_label and response_result:
                    paragraph_stats["error_wrong"] += 1
                    # 记录整条数据到错误条目中
                    paragraph_error_items["error_wrong"].append(copy.deepcopy(data))

            # ===== 声明级别 =====
            claims_label_list = data.get("claims_factuality_label", [])
            claims_result_list = data.get("claims_factuality_result", [])
            for lbl, rst in zip(claims_label_list, claims_result_list):
                if isinstance(lbl, bool) and isinstance(rst, bool):
                    claims_stats["total"] += 1
                    if lbl and rst:
                        claims_stats["correct_correct"] += 1
                    elif lbl and not rst:
                        claims_stats["correct_wrong"] += 1
                    elif not lbl and not rst:
                        claims_stats["error_correct"] += 1
                    elif not lbl and rst:
                        claims_stats["error_wrong"] += 1

    # --- 3) 构建整体统计结果（第一行） ---
    analysis_result = {
        "paragraph_level": paragraph_stats,
        "claims_level": claims_stats
    }

    # --- 4) 写出 JSONL ---
    with open(output_file, 'w', encoding='utf-8') as fout:
        # 第 1 行：写总统计结果（完整的段落级别 & 声明级别）
        fout.write(json.dumps(analysis_result, ensure_ascii=False) + "\n")

        # 后续行：只写段落级别有错误的条目
        # 两种错误：correct_wrong (T,F) 和 error_wrong (F,T)
        # 如果需要自定义显示文字，可在下面进行映射
        category_mapping = {
            "correct_wrong": "段落级别错误(T,F)",
            "error_wrong": "段落级别错误(F,T)"
        }

        # 先输出 correct_wrong，再输出 error_wrong
        for cat_key in ["correct_wrong", "error_wrong"]:
            for item_data in paragraph_error_items[cat_key]:
                # 在输出时，添加一个 'error_category' 字段，以保留原始所有字段
                out_obj = item_data
                out_obj["error_category"] = category_mapping[cat_key]
                fout.write(json.dumps(out_obj, ensure_ascii=False) + "\n")

    print(f"分析完成，结果已写入: {output_file}")


if __name__ == "__main__":
    input_file_path = "output_clean0101_processed.jsonl"
    output_file_path = "analysis_result.jsonl"
    analyze_output_file_to_jsonl(input_file_path, output_file_path)
