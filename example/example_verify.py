import json
import os
from factool.factool_verify import FactoolVerify
from path_config import LABEL_FILE, DETECT_FILE

os.environ['OPENAI_API_KEY'] = "sk-lH0YfSFt0PrQMSBHTTjM3V03qgGTf1oXAMnG2Mfwkmckuqdl"
os.environ['SERPER_API_KEY'] = "71a9a751fba127c347e7f41bd261d4370beee90b"
os.environ['SCRAPER_API_KEY'] = "73ace7682c4a312c68973be4cc1229f3"
os.environ['OPENAI_API_BASE'] = "https://api.chatanywhere.tech/v1"
# 初始化 FactoolVerify 实例
# factool_verify_instance = FactoolVerify("gpt-3.5-turbo-0125")

# 定义输入和输出文件路径
input_file = LABEL_FILE
output_file = DETECT_FILE


def read_lines_from_jsonl(jsonl_file_path, start_line=1, end_line=None):
    """
    从 jsonl 文件中按行区间读取数据，行号从 1 开始。
    :param jsonl_file_path: jsonl文件路径
    :param start_line: 起始行（含），默认 1 表示第一行
    :param end_line: 结束行（不含），如果为 None 表示读到文件结束
    :return: 按行区间获取到的 list
    """
    data_list = []
    with open(jsonl_file_path, 'r', encoding='utf-8') as f:
        # 从行号 1 开始计数
        for idx, line in enumerate(f, start=1):
            # 跳过未到达 start_line 的行
            if idx < start_line:
                continue
            # 超过或等于 end_line 后停止
            if end_line is not None and idx >= end_line:
                break

            data = json.loads(line.strip())
            data_list.append(data)
    return data_list


def append_result_to_file(result, output_file_path):
    """
    将单条 result 以 jsonl 的方式追加写入到文件，不覆盖原有内容
    :param result: dict，需要写入的一条结果
    :param output_file_path: 输出文件路径
    """
    with open(output_file_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(result, ensure_ascii=False) + '\n')


def main():
    # 初始化 FactoolVerify 实例
    factool_verify_instance = FactoolVerify("gpt-3.5-turbo-0125")

    # 示例：读取从第 1 行（start_line=1）到第 5 行（end_line=6）【不包含第 6 行】
    start_line = 37
    end_line = 95
    data_list = read_lines_from_jsonl(input_file, start_line=start_line, end_line=end_line)

    # 依次处理 data_list 中的每条数据
    for i, item in enumerate(data_list, start=1):
        # run_verification 返回的是一个 list，这里只传入一条 item，所以返回只有一个结果
        result_list = factool_verify_instance.run_verification([item])
        single_result = result_list[0]

        # 追加写入
        append_result_to_file(single_result, output_file)

        # 打印进度
        print(f"已完成从第 {start_line} 行到第 {end_line-1} 行的处理")
        print(f"已完成共计 {i} 条处理")


if __name__ == "__main__":
    main()
