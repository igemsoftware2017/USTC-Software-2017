from rest_framework.decorators import api_view
from rest_framework.response import Response
from .analyzer import analyzer


@api_view(['GET'])
def analyze(request, part_name):
    result = analyzer.analyze(part_name)

    return Response({
        'nodes': result.nodes,
        'edges': result.edges
    })


@api_view(['GET'])
def analyze_reverse(request, part_name):

    result = analyzer.analyze_reverse(part_name)

    return Response({
        'nodes': result.nodes,
        'edges': result.edges
    })
