# coding=utf-8
"""
This is the view to convert a true/false string to a circuit.
URI:/biocircuit/string
method:get
"""
__author__ = 'ctyi'

from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ParseError
from rest_framework import status
from rest_framework import serializers

from . import biocircuit as biocircuit
from .biogate_man import load_gates_json, biogate
from . import bio_system as biosystem
from . import bio_system_cache as cache
from biohub.biobrick.models import Part as Parts


class BiocircuitView(APIView):
    """This URI return a series of circuit with score.

    Usage:
    """
    parser_classes = (JSONParser,)
    renderer_classes = (JSONRenderer,)

    def get(self, request, string, format=None):
        """
        request: GET /biocircuit/ID
        response: json api_circuit
        """
        try:
            digit_count = len([c for c in string if c in ('0', '1')])
            if digit_count < 2:
                raise ParseError(detail="At least two digits are required.")
            expr = biocircuit.string2expr(string)
            circuit = biocircuit.create_circuit(expr)
            scores = biocircuit.circuit_score(circuit, biogate.d_gate)
            response_dict = biocircuit.api_circuit(circuit, scores)
            return Response(response_dict)

        except BaseException as error:
            # raise
            response = {}
            response["status"] = "failed"
            response["detail"] = str(error)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class ScoreView(APIView):
    """This API could calc the score of a circuit

    """
    parser_classes = (JSONParser,)
    renderer_classes = (JSONRenderer,)

    def post(self, request, format=None):
        """
        request: POST /biocircuit/score/
        Response: json
                {
                    status:"SUCCESS"
                    score: float
                }
        """
        try:
            nodes = request.data['nodes']
            score = biocircuit.calc_score(nodes, biogate.d_gate)
            response = {}
            response["status"] = "SUCCESS"
            response["score"] = score
            return Response(response)
        except BaseException as error:
            # raise
            response = {}
            response["status"] = "failed"
            response["detail"] = str(error)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class GatesView(APIView):
    parser_classes = (JSONParser,)
    renderer_classes = (JSONRenderer,)

    def get(self, request):
        try:
            return Response(load_gates_json())
        except Exception as error:
            response = {}
            response["status"] = "failed"
            response["detail"] = error.__doc__
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class SimulateView(APIView):
    """URI /simulate return the simulate result of a biological circuit

    Usage:
    """
    parser_classes = (JSONParser,)
    renderer_classes = (JSONRenderer,)

    def post(self, request, format=None):
        """Only accept application/json type.

        """
        try:
            # request.data is the graph of the bio-system
            '''
            system_data = biosystem.bio_system(request.data)
            cache_data = cache.biosystem_cache(request.data)
            if cache_data:  # != None, better not compare with None.
                response_from_back = cache_data
            else:
                system_data.simulation()
                response_from_back = system_data.record_list
                cache.biosystem_update_cache(request.data, response_from_back)
            '''
            cache_data = cache.biosystem_cache(request.data)
            if cache_data:  # != None, better not compare with None.
                response_from_back = cache_data
            else:
                response_from_back = biosystem.simulate(request.data)
                cache.biosystem_update_cache(request.data, response_from_back)
        except BaseException as error:
            raise
            response = {"status": "failed", "detail": error.message}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        # assert isinstance(response_from_back, list)
        return Response(response_from_back)


class PartsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parts


class PartsView(APIView):
    """This URI return frontend parts info in the database.

    Usage:
    """
    parser_classes = (JSONParser,)
    renderer_classes = (JSONRenderer,)

    def post(self, request, format=None):
        """
        deal with the POST method only
        """
        response_total = []
        for item in request.data:
            pre_filter = {}
            if "id" in item:
                pre_filter['id'] = item['id']
            for key in item:
                if key != "id":
                    pre_filter[key + "__contains"] = item[key]
            queryset = Parts.objects.filter(**pre_filter)
            serializer = PartsSerializer(queryset, many=True)
            response_total.extend(serializer.data)
        response_dict = {}
        response_dict['status'] = "SUCCESS"
        response_dict['data'] = response_total
        return Response(response_dict)
