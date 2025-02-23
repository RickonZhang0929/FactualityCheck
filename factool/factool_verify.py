import asyncio

import json


from factool.knowledge_qa.pipeline_verify import knowledge_qa_pipeline

class FactoolVerify():
    def __init__(self, foundation_model):
        self.foundation_model = foundation_model
        self.pipelines = {
            "kbqa_online": knowledge_qa_pipeline(  # 添加验证管道
                foundation_model, 10, "online"
            )
        }


    def extract_lists(self, data):
        """
        从单个数据中提取声明列表和证据列表
        :param data: 包含数据的字典
        :return: 声明列表和证据列表
        """
        claims_lists = data.get("claims", [])
        evidences_lists = data.get("evidence", [])
        return claims_lists, evidences_lists

    def run_verification(self, data_list):
        """
        主函数，协调从文件提取列表以及执行验证步骤，并将结果与原数据的 prompt 合并
        """
        all_results = []
        for data in data_list:
            claims_lists, evidences_lists = self.extract_lists(data)
            verifications = asyncio.run(self.pipelines["kbqa_online"].verification_only(claims_lists, evidences_lists))
            # 将验证结果和原数据中的 prompt 合并为一个对象
            result_obj = {**data, "verifications": verifications}
            all_results.append(result_obj)
        return all_results
