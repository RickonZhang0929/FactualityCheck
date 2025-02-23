import json
from path_config import DETECT_FILE, CLEAN_FILE

def read_lines_from_jsonl(jsonl_file_path, num_lines=None):
    """
    从 jsonl 文件中读取相应行数的数据
    :param jsonl_file_path: jsonl 文件的路径
    :param num_lines: 要读取的行数，默认为 None，即读取全部行
    :return: 存储读取的数据的列表
    """
    data_list = []
    line_count = 0
    with open(jsonl_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if num_lines is not None and line_count >= num_lines:
                break
            data = json.loads(line)
            data_list.append(data)
            line_count += 1
    return data_list


def write_results_to_file(results, output_file_path):
    """
    将结果写入输出文件，一行是一个对象
    :param results: 包含结果的列表
    :param output_file_path: 输出文件的路径
    """
    with open(output_file_path, 'w', encoding='utf-8') as file:
        for result in results:
            file.write(json.dumps(result, ensure_ascii=False) + '\n')


def process(data_list):
    """
    按照要求处理数据列表
    :param data_list: 从输入文件读取的数据列表，每个元素为一个字典格式的数据
    :return: (处理后的结果列表，每个元素为按照要求整理后的字典, 错误列表)
    """
    result_list = []
    error_list = []  # 用于记录出错的数据（只保留 prompt）

    for index, data in enumerate(data_list, start=1):  # 从1开始定义序号id
        try:
            new_result = {
                "id": index,
                "prompt": data["prompt"],
                "response_factuality_label": data["response_factuality"],
                "response_factuality_result": None,  # 先初始化为 None
                "claims_factuality_label": data["claims_factuality_label"],
                "claims_factuality_result": []
            }

            # 提取并整理 claims_factuality_result
            # 可能有些 data["verifications"] 是 None 或结构不对，这里用 try/except
            claims_factuality_result = [
                verification[0]["factuality"]
                for verification in data["verifications"]
                if verification and isinstance(verification, list) and len(verification) > 0 and "factuality" in verification[0]
            ]
            # 如果 verifications 里出现不符合的结构，最终会导致 claims_factuality_result 与 claims_factuality_label 长度不一致等
            # 这里可以根据实际需求做进一步的判断或处理

            new_result["claims_factuality_result"] = claims_factuality_result

            # 根据 claims_factuality_result 计算 response_factuality_result
            response_factuality_result = all(claims_factuality_result)
            new_result["response_factuality_result"] = response_factuality_result

            # 一切成功则加入 result_list
            result_list.append(new_result)

        except Exception as e:
            # 如果出现任何异常，就把 prompt 加入错误列表，跳过此条
            error_list.append(data.get("prompt", "缺少 prompt 字段"))

    return result_list, error_list


# 定义输入和输出文件路径
input_file = DETECT_FILE
output_file = CLEAN_FILE


def main():
    data_list = read_lines_from_jsonl(input_file, 93)
    result, error_list = process(data_list)
    write_results_to_file(result, output_file)
    print(f"完成了 {len(result)} 条记录整理")

    # 将错误列表打印出来（只保留 prompt）
    if error_list:
        print("以下记录在处理时出现错误，已被跳过：")
        for err_prompt in error_list:
            print(err_prompt)


if __name__ == "__main__":
    main()
