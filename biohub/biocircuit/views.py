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

from . import biocircuit as biocircuit
from .biogate_man import load_gates_json, biogate


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
