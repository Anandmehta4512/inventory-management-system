class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.product_data = None

class ProductTrie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str, product_data: dict):
        node = self.root
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        node.product_data = product_data

    def search_prefix(self, prefix: str, limit: int = 5) -> list:
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return []
            node = node.children[char]
        
        results = []
        self._dfs(node, results, limit)
        return results

    def _dfs(self, node: TrieNode, results: list, limit: int):
        if len(results) >= limit:
            return
        if node.is_end_of_word and node.product_data:
            results.append(node.product_data)
        for char, child in sorted(node.children.items()):
            self._dfs(child, results, limit)
