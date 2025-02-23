import os
import asyncio
import aiohttp
import uuid

os.environ['ZHIPU_API_KEY'] = "ea833bbecf3ee7771fc5bb9b15486fb4.NeDaYr1io0KkM08o"


class ZhipuWebSearchAPIWrapper:
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
            "Authorization": self.api_key,
            "Content-Type": "application/json",
        }
        data = {
            "request_id": str(uuid.uuid4()),
            "tool": self.tool,
            "stream": False,
            "messages": [{"role": "user", "content": search_term}]
        }

        async with session.post(self.url, json=data, headers=headers) as response:
            response_data = await response.json()
            return response_data

    def _parse_results(self, results):
        snippets = []

        if 'choices' in results and results['choices']:
            search_results = results['choices'][0]['message'].get('tool_calls', [])[1].get('search_result', [])
            for result in search_results:
                element = {"content": result['content'], "source": result.get('link', 'None')}
                snippets.append(element)

        if len(snippets) == 0:
            element = {"content": "No good search result was found", "source": "None"}
            return [element]

        return snippets[:self.k]

    async def parallel_searches(self, search_queries):
        async with aiohttp.ClientSession() as session:
            tasks = [self._zhipu_web_search_results(session, query) for query_group in search_queries for query in
                     query_group]
            search_results = await asyncio.gather(*tasks, return_exceptions=True)
            return search_results

    async def run(self, query_groups):
        """Run query groups through Zhipu web-search-pro and parse results."""
        results_by_group = []
        for query_group in query_groups:
            results = await self.parallel_searches([query_group])
            snippets_list = []
            for result in results:
                if result is not None:
                    snippets_list.append(self._parse_results(result))
                else:
                    snippets_list.append([{"content": "No valid response", "source": "None"}])
            results_by_group.append(snippets_list)
        return results_by_group

    def format_results(self, snippets_split):
        """Format the results to match the new required output format."""
        formatted_results = []
        for snippet_group in snippets_split:
            formatted_group = []
            for snippets in snippet_group:
                for snippet in snippets:
                    formatted_snippet = {
                        "content": snippet["content"],
                        "source": snippet["source"],
                    }
                    formatted_group.append(formatted_snippet)
            formatted_results.append(formatted_group)
        return formatted_results

    async def run_format(self, query_groups):
        """Run the query groups and return formatted results."""
        snippets_split = await self.run(query_groups)
        formatted_results = self.format_results(snippets_split)
        return formatted_results


if __name__ == "__main__":
    os.environ['ZHIPU_API_KEY'] = "ea833bbecf3ee7771fc5bb9b15486fb4.NeDaYr1io0KkM08o"

    search = ZhipuWebSearchAPIWrapper()

    queries = [['What is 985 schools in China?', 'Is Tsinghua University a 985 school?'],
               ['Location of Tsinghua University', 'Tsinghua University address'],
               ['Is Tsinghua University a comprehensive research university?', 'Tsinghua University research focus'],
               ['清华大学成立年份', '清华大学创办时间'],
               ['What is the predecessor of Tsinghua University?', 'Tsinghua University predecessor']]

    formatted_results = asyncio.run(search.run_format(queries))
    print(formatted_results)
