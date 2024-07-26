import asyncio
import copy

# import med_doc_qa_pipeline_confidence
from factool.code.pipeline import code_pipeline
from factool.knowledge_qa.pipeline_confidence import knowledge_qa_pipeline_confidence
from factool.math.pipeline import math_pipeline
from factool.med_doc_qa.pipeline import med_doc_qa_pipeline
from factool.scientific.pipeline import scientific_pipeline



class FactoolConfidence():
    def __init__(self, foundation_model):
        self.foundation_model = foundation_model
        self.pipelines = {
            "kbqa_online": knowledge_qa_pipeline_confidence(
                foundation_model, 10, "online"
            ),
            "code": code_pipeline(
                foundation_model, 3, 3
            ),
            "math": math_pipeline(
                foundation_model
            ),
            "scientific": scientific_pipeline(
                foundation_model
            ),
            "med_doc_qa": med_doc_qa_pipeline(
                foundation_model
            )
        }

    def run(self, inputs):
        outputs = copy.deepcopy(inputs)
        batches = []
        current_category = inputs[0]['category']
        current_search_type = inputs[0].get('search_type', None)
        current_data_link = inputs[0].get('data_link', None)
        current_embedding_link = inputs[0].get('embedding_link', None)
        current_batch = []

        for input in inputs:
            if (input['category'] == current_category != 'kbqa') \
                    or (input['category'] == current_category == 'kbqa' and input.get('search_type',
                                                                                      None) == current_search_type == "online") \
                    or (input['category'] == current_category == 'kbqa' and input.get('search_type',
                                                                                      None) == current_search_type == "local" \
                        and input.get('data_link', None) == current_data_link and input.get('embedding_link',
                                                                                            None) == current_embedding_link):
                current_batch.append(input)
            else:
                batches.append(current_batch)
                current_batch = [input]
                current_category = input['category']
                current_search_type = input.get('search_type', None)
                current_data_link = input.get('data_link', None)
                current_embedding_link = input.get('embedding_link', None)

        batches.append(current_batch)  # append the last batch

        index = 0
        for batch in batches:
            if not batch: continue
            category = batch[0]['category']
            search_type = batch[0].get('search_type', None)
            if category == 'code':
                batch_results = asyncio.run(
                    self.pipelines[category].run_with_tool_api_call(
                        [sample['prompt'] for sample in batch],
                        [sample['response'] for sample in batch],
                        [sample['entry_point'] for sample in batch]
                    )
                )
            elif category == 'kbqa':
                if search_type is None or search_type == "online":
                    batch_results = asyncio.run(
                        self.pipelines[category + "_online"].run_with_tool_api_call(
                            [sample['prompt'] for sample in batch],
                            [sample['response'] for sample in batch],
                        )
                    )
                else:
                    batch_results = asyncio.run(
                        knowledge_qa_pipeline_confidence(
                            self.foundation_model, 2, "local", batch[0].get("data_link"), batch[0].get("embedding_link")
                        ).run_with_tool_api_call(
                            [sample['prompt'] for sample in batch],
                            [sample['response'] for sample in batch],
                        )
                    )
            else:
                batch_results = asyncio.run(
                    self.pipelines[category].run_with_tool_api_call(
                        [sample['prompt'] for sample in batch],
                        [sample['response'] for sample in batch]
                    )
                )
            for result in batch_results:
                outputs[index].update(result)
                index += 1

        # calculate average response_level_factuality
        total_response_factuality = sum(output['response_level_factuality'] == True for output in outputs)
        avg_response_level_factuality = total_response_factuality / len(outputs)

        # calculate average claim_level_factuality
        num_claims = 0
        total_claim_factuality = 0
        for output in outputs:
            num_claims += len(output['claim_level_factuality'])
            if output['category'] == 'kbqa':
                if output['claim_level_factuality'] != []:
                    total_claim_factuality += sum(claim['factuality'] == True if claim != None else 0 for claim in
                                                  output['claim_level_factuality'])
                else:
                    total_claim_factuality += 0
            elif output['category'] == 'code':
                total_claim_factuality += (output['claim_level_factuality'] == True)
            elif output['category'] == 'math':
                total_claim_factuality += sum(
                    claim_factuality == True for claim_factuality in output['claim_level_factuality'])
            elif output['category'] == 'scientific':
                total_claim_factuality += sum(claim['factuality'] == True for claim in output['claim_level_factuality'])

        avg_claim_level_factuality = total_claim_factuality / num_claims

        # calculate final claim factuality confidence
        for output in outputs:
            if output['claim_level_factuality']:
                output['claim_factuality_confidence'] = self.calculate_final_confidence(
                    output['claim_level_factuality'])

        return {"average_claim_level_factuality": avg_claim_level_factuality,
                "average_response_level_factuality": avg_response_level_factuality, "detailed_information": outputs}

    def calculate_final_confidence(self, verifications_in_responses):
        b = 0.7  # 超参数
        k = 0.2  # 保留比例

        weighted_confidences = []
        total_importance = 0
        for i, verification in enumerate(verifications_in_responses):
            importance = verification.get('importance', 0)
            confidence = verification.get('confidence', 0)
            factuality = verification.get('factuality', False)
            factuality_num = 1 if factuality else 0  # 将 true 和 false 转换为 1 和 0

            partial_confidence = b * confidence + (1 - b) * (factuality_num + k * (1 - factuality_num))
            weighted_confidence = importance * partial_confidence
            weighted_confidences.append(weighted_confidence)
            total_importance += importance

            # 输出计算过程
            print(f"声明 {i + 1}:")
            print(f"重要性评分 (importance_i) = {importance}")
            print(f"验证置信度评分 (confidence_i) = {confidence}")
            print(f"判断结果分数 (factuality_i) = {factuality} ({factuality_num})")
            print(
                f"部分综合置信度评分 = {importance} * ({b} * {confidence} + (1 - {b}) * ({factuality_num} + {k} * (1 - {factuality_num}))) = {weighted_confidence}")
            print()

        final_confidence = sum(weighted_confidences) / total_importance if total_importance > 0 else 0

        # 输出归一化处理过程
        print(f"未归一化的综合置信度评分 = {sum(weighted_confidences)}")
        print(f"总重要性评分 = {total_importance}")
        print(f"归一化后的综合置信度评分 = {final_confidence}")
        print()

        return final_confidence
