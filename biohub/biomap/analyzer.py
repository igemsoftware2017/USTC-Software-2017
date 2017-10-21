class _Result:

    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.too_large = False

    def add_edge(self, source, target):

        self.edges.append({
            'source': source,
            'target': target,
            'value': 1
        })

    def mark_visited(self, node):
        self._visited[node] = True

    def add_node(self, node, group):
        self.nodes[node] = group

    def is_visited(self, node):
        return node in self.nodes


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

    def analyze_reverse(self, part_name):

        result = _Result()

        self._analyze_reverse(part_name, result)

        return result

    def _analyze_reverse(self, part_name, result):

        result.add_node(part_name, 0)

        self._builder.build(part_name)
        parts = self._storage.srandmember('rev_' + part_name, 101)

        counter = 0
        for part in parts:

            counter += 1

            if str(part) == '0':
                continue

            result.add_node(part, 1)
            result.add_edge(part, part_name)

        if counter == 101:
            result.too_large = True

    def _analyze(self, part_name, depth, result):

        if depth < 0 or result.is_visited(part_name):
            return

        result.add_node(part_name, depth)

        self._builder.build(part_name)
        subparts = self._storage.smembers(part_name)

        for subpart in subparts:
            if str(subpart) == '0':
                continue

            result.add_edge(part_name, subpart)
            self._analyze(subpart, depth - 1, result)


analyzer = Analyzer()
