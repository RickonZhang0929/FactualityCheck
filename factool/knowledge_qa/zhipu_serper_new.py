import os
import asyncio
import aiohttp
import uuid

os.environ['ZHIPU_API_KEY'] = "ea833bbecf3ee7771fc5bb9b15486fb4.NeDaYr1io0KkM08o"


class ZhipuWebSearchAPIWrapperNew:
    """Wrapper around the Zhipu web-search-pro API."""

    def __init__(self, snippet_cnt=10) -> None:
        self.k = snippet_cnt
        self.api_key = os.environ.get("ZHIPU_API_KEY", None)
        assert self.api_key is not None, "Please set the ZHIPU_API_KEY environment variable."
        assert self.api_key != '', "Please set the ZHIPU_API_KEY environment variable."
        self.url = "https://open.bigmodel.cn/api/paas/v4/tools"
        self.tool = "web-search-pro"

    async def _zhipu_web_search_results(self, session, search_term: str) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "request_id": str(uuid.uuid4()),  # 生成唯一请求ID
            "tool": self.tool,
            "stream": False,  # 关闭流式返回
            "messages": [{"role": "user", "content": search_term}]  # 正确的消息格式
        }

        print("Sending request to Zhipu AI...")
        async with session.post(self.url, json=data, headers=headers) as response:
            print(f"Response status: {response.status}")
            response_data = await response.json()
            print(f"Response data: {response_data}")
            return response_data

    def _parse_results(self, results):
        snippets = []
        # 检查 Zhipu AI 返回的搜索结果
        if 'choices' in results and results['choices']:
            tool_calls = results['choices'][0]['message'].get('tool_calls', [])
            if len(tool_calls) > 0:
                search_results = tool_calls[0].get('search_result', [])
                for result in search_results:
                    element = {
                        "content": result.get('content', 'No content'),
                        "source": result.get('link', 'No link')
                    }
                    snippets.append(element)
            else:
                snippets.append({"content": "No search results found", "source": "None"})
        else:
            snippets.append({"content": "No valid response from Zhipu AI", "source": "None"})

        # 返回最多 k 条搜索结果
        return snippets[:self.k]

    async def parallel_searches(self, search_queries):
        async with aiohttp.ClientSession() as session:
            tasks = [self._zhipu_web_search_results(session, query) for query in search_queries]
            search_results = await asyncio.gather(*tasks, return_exceptions=True)
            return search_results

    async def run(self, queries):
        """Run query through Zhipu web-search-pro and parse result."""
        # 保证queries中的每个元素都是完整的查询语句，而不是单个字符
        flattened_queries = [query for query in queries if query]

        results = await self.parallel_searches(flattened_queries)
        snippets_list = []
        for i in range(len(results)):
            if results[i] is not None and not isinstance(results[i], Exception):
                snippets_list.append(self._parse_results(results[i]))
            else:
                snippets_list.append([{"content": "No valid response", "source": "None"}])

        return snippets_list

    def format_results(self, snippets_split):
        """Format the results to match the original Google Serper API output format."""
        formatted_results = []
        for snippet_group in snippets_split:
            formatted_group = []
            for snippet in snippet_group:
                formatted_snippet = {
                    "content": snippet["content"],
                    "source": snippet["source"],
                }
                formatted_group.append(formatted_snippet)
            formatted_results.append(formatted_group)
        return formatted_results

    async def run_format(self, queries):
        """Run the query and return formatted results."""
        snippets_split = await self.run(queries)
        formatted_results = self.format_results(snippets_split)
        return formatted_results


if __name__ == "__main__":
    search = ZhipuWebSearchAPIWrapperNew()
    queries = ["What is the capital of the United States?"]

    formatted_results = asyncio.run(search.run_format(queries))
    print(formatted_results)
