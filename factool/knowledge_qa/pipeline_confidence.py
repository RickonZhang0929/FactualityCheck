import json
import yaml
import os
import time
import math
import pdb
from typing import List, Dict

from factool.knowledge_qa.tool import google_search
from factool.knowledge_qa.tool import local_search
from factool.utils.base.pipeline import pipeline

class knowledge_qa_pipeline_confidence(pipeline):
    def __init__(self, foundation_model, snippet_cnt, search_type, data_link=None, Embed_link=None):
        super().__init__('knowledge_qa', foundation_model)
        if (search_type == 'online'):
            self.tool = google_search(snippet_cnt=snippet_cnt)
        elif (search_type == 'local'):
            self.tool = local_search(snippet_cnt=snippet_cnt, data_link=data_link, embedding_link=Embed_link)
        with open(os.path.join(self.prompts_path, "claim_extraction_with_confidence.yaml"), 'r') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
        self.claim_prompt = data['knowledge_qa']

        with open(os.path.join(self.prompts_path, 'query_generation_with_confidence.yaml'), 'r') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
        self.query_prompt = data['knowledge_qa']

        with open(os.path.join(self.prompts_path, 'agreement_verification_with_confidence.yaml'), 'r') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
        self.verification_prompt = data['knowledge_qa']

    async def _claim_extraction(self, responses):
        messages_list = [
            [
                {"role": "system", "content": self.claim_prompt['system']},
                {"role": "user", "content": self.claim_prompt['user'].format(input=response)},
            ]
            for response in responses
        ]
        return await self.chat.async_run(messages_list, List)

    async def _query_generation(self, claims):
        if claims == None:
            return ['None']
        messages_list = [
            [
                {"role": "system", "content": self.query_prompt['system']},
                {"role": "user",
                 "content": self.query_prompt['user'].format(input=claim['claim'] if 'claim' in claim else '')},
            ]
            for claim in claims
        ]
        return await self.chat.async_run(messages_list, List)

    async def _verification(self, claims, evidences):
        messages_list = [
            [
                {"role": "system", "content": self.verification_prompt['system']},
                {"role": "user",
                 "content": self.verification_prompt['user'].format(claim=claim['claim'], evidence=str(evidence))},
            ]
            for claim, evidence in zip(claims, evidences)
        ]
        return await self.chat.async_run(messages_list, dict)

    async def run_with_tool_live(self, responses):
        claims_in_responses = await self._claim_extraction(responses)
        queries_in_responses = []
        evidences_in_responses = []
        sources_in_responses = []
        verifications_in_responses = []
        for claims_in_response in claims_in_responses:
            queries = await self._query_generation(claims_in_response)
            queries_in_responses.append(queries)
            search_outputs_for_claims = await self.tool.run(queries)
            evidences = [[output['content'] for output in search_outputs_for_claim] for search_outputs_for_claim in
                         search_outputs_for_claims]
            evidences_in_responses.append(evidences)
            sources = [[output['source'] for output in search_outputs_for_claim] for search_outputs_for_claim in
                       search_outputs_for_claims]
            sources_in_responses.append(sources)
            verifications = await self._verification(claims_in_response, evidences)
            verifications_in_responses.append(verifications)

        return claims_in_responses, queries_in_responses, evidences_in_responses, sources_in_responses, verifications_in_responses

    async def run_with_tool_api_call(self, prompts, responses):
        batch_size = 5
        num_batches = math.ceil(len(prompts) / batch_size)

        self.sample_list = [{"prompt": prompt, "response": response, "category": 'kbqa'} for prompt, response in
                            zip(prompts, responses)]

        for i in range(num_batches):
            print(i)
            batch_start = i * batch_size
            batch_end = min((i + 1) * batch_size, len(responses))

            claims_in_responses, queries_in_responses, evidences_in_responses, sources_in_responses, verifications_in_responses = await self.run_with_tool_live(
                responses[batch_start:batch_end])

            for j, (claims_in_response, queries_in_response, evidences_in_response, sources_in_response,
                    verifications_in_response) in enumerate(
                    zip(claims_in_responses, queries_in_responses, evidences_in_responses, sources_in_responses,
                        verifications_in_responses)):
                index = batch_start + j

                if claims_in_response != None:
                    for k, claim in enumerate(claims_in_response):
                        if verifications_in_response[k] != None:
                            if claim != None:
                                verifications_in_response[k].update(
                                    {'claim': claim['claim'], 'importance': claim['importance']})
                            else:
                                verifications_in_response[k].update({'claim': 'None', 'importance': 0})

                evidences_with_source = []
                for evidence, source in zip(evidences_in_response, sources_in_response):
                    evidences_with_source.append({'evidence': evidence, 'source': source})
                self.sample_list[index].update({
                    'claims': claims_in_response,
                    'queries': queries_in_response,
                    'evidences': evidences_with_source,
                    'claim_level_factuality': verifications_in_response,
                    'response_level_factuality': all(
                        [verification['factuality'] if verification != None else True for verification in
                         verifications_in_response])
                })

        return self.sample_list
