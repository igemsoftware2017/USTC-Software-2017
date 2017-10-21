class _Result:

    def __init__(self):
        self._mapping = {}
        self._visited = {}
        self.nodes = []
        self.edges = []

    def get_node_index(self, node):

        if node in self._mapping:
            return self._mapping[node]

        self.nodes.append({'name': node})
        index = self._mapping[node] = len(self.nodes) - 1
        return index

    def add_edge(self, source, target):

        self.edges.append({
            'source': self.get_node_index(source),
            'target': self.get_node_index(target)
        })

    def mark_visited(self, node):
        self.get_node_index(node)
        self._visited[node] = True

    def is_visited(self, node):
        return node in self._visited


class Analyzer:

    def __init__(self):

        from biohub.biomap.storage import storage
        from biohub.biomap.builder import builder

        self._storage = storage
        self._builder = builder

    def analyze(self, part_name, max_depth=100):

        if max_depth < 1:
            max_depth = 1
        elif max_depth > 100:
            max_depth = 100

        result = _Result()

        self._analyze(part_name, max_depth, result)

        return result

    def analyze_reverse(self, part_name, max_depth=100):

        if max_depth < 1:
            max_depth = 1
        elif max_depth > 100:
            max_depth = 100

        result = _Result()

        self._analyze_reverse(part_name, max_depth, result)

        return result

    def _analyze_reverse(self, part_name, depth, result):

        if depth < 0 or result.is_visited(part_name):
            return

        result.mark_visited(part_name)

        self._builder.build(part_name)
        parts = self._storage.smembers('rev_' + part_name)

        for part in parts:

            if str(part) == '0':
                continue

            result.add_edge(part, part_name)
            self._analyze(part_name, depth - 1, result)

    def _analyze(self, part_name, depth, result):

        if depth < 0 or result.is_visited(part_name):
            return

        result.mark_visited(part_name)

        self._builder.build(part_name)
        subparts = self._storage.smembers(part_name)

        for subpart in subparts:
            if str(subpart) == '0':
                continue

            result.add_edge(part_name, subpart)
            self._analyze(part_name, depth - 1, result)


analyzer = Analyzer()
