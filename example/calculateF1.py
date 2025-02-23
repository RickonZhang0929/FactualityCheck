import json
from sklearn.metrics import classification_report, f1_score


def calculate_response_metrics(filename):
    true_labels = []
    pred_labels = []
    line_num = 0

    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            line_num += 1
            line = line.strip()
            if not line:
                # 跳过空行
                continue
            try:
                data = json.loads(line)
                true_labels.append(int(data['response_factuality_label']))
                pred_labels.append(int(data['response_factuality_result']))
            except json.JSONDecodeError as e:
                print(f"JSON解析错误在第 {line_num} 行: {e}")
                print(f"内容: {line}")
                continue
            except KeyError as e:
                print(f"缺少键 {e} 在第 {line_num} 行。")
                print(f"内容: {line}")
                continue
            except ValueError as e:
                print(f"值转换错误在第 {line_num} 行: {e}")
                print(f"内容: {line}")
                continue

    if not true_labels or not pred_labels:
        print("没有有效的response标签可用于计算指标。")
        return

    print("### Response 详细分类报告 ###")
    report = classification_report(true_labels, pred_labels, target_names=['False', 'True'])
    print(report)

    # 如果只需要F1分数
    f1 = f1_score(true_labels, pred_labels)
    print(f"Response F1 Score: {f1:.4f}\n")


def calculate_claims_metrics(filename):
    true_labels = []
    pred_labels = []
    line_num = 0

    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            line_num += 1
            line = line.strip()
            if not line:
                # 跳过空行
                continue
            try:
                data = json.loads(line)
                # 确保 claims_factuality_label 和 claims_factuality_result 长度相同
                if len(data['claims_factuality_label']) != len(data['claims_factuality_result']):
                    print(f"第 {line_num} 行中 claims 的标签和结果长度不一致。")
                    print(f"内容: {line}")
                    continue
                true_labels.extend([int(label) for label in data['claims_factuality_label']])
                pred_labels.extend([int(result) for result in data['claims_factuality_result']])
            except json.JSONDecodeError as e:
                print(f"JSON解析错误在第 {line_num} 行: {e}")
                print(f"内容: {line}")
                continue
            except KeyError as e:
                print(f"缺少键 {e} 在第 {line_num} 行。")
                print(f"内容: {line}")
                continue
            except ValueError as e:
                print(f"值转换错误在第 {line_num} 行: {e}")
                print(f"内容: {line}")
                continue

    if not true_labels or not pred_labels:
        print("没有有效的claims标签可用于计算指标。")
        return

    print("### Claims 详细分类报告 ###")
    report = classification_report(true_labels, pred_labels, target_names=['False', 'True'])
    print(report)

    # 如果只需要F1分数
    f1 = f1_score(true_labels, pred_labels)
    print(f"Claims F1 Score: {f1:.4f}\n")


def main():
    filename = 'calcu_test.jsonl'
    calculate_response_metrics(filename)
    calculate_claims_metrics(filename)


if __name__ == "__main__":
    main()
