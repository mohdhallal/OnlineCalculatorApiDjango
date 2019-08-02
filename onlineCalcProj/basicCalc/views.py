from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from .calculator import Calculator
from .serializer import CalculatorResponseSerializer,CalculatorPostSerializer
from rest_framework.views import APIView
from operationsHistory.models import History
from rest_framework.generics import GenericAPIView

# ------------for UI docs-----------
from rest_framework.filters import BaseFilterBackend
import coreapi

class SimpleFilterBackend(BaseFilterBackend):
    def get_schema_fields(self, view):
        return [coreapi.Field(
            name='expression',
            location='query',
            required=True,
            type='string'
        )]
#------------------------------------

class OnlineCalculator(GenericAPIView):
       filter_backends = (SimpleFilterBackend,)
       def get_serializer_class(self,*args,**kwargs):
              if self.request.method == 'POST':
                     return CalculatorPostSerializer
              return CalculatorResponseSerializer
       def __init__(self):
              self.__result=None
              self.__expression=None


       def __useCalculator(self):
              calculator=Calculator()
              self.__expression=str(self.__expression).replace('\'','').replace('\"','')
              result=calculator.calculate(self.__expression)
              return result

       def __getSerializedResult(self):

              calculatorResponseSerializer=CalculatorResponseSerializer(data=self.__result)
              if calculatorResponseSerializer.is_valid(): 
                    return calculatorResponseSerializer.data
              else:
                     return calculatorResponseSerializer.errors

       def __saveHistory(self):

              print(self.__result)
              opsHistory=History(
                     expression=self.__expression,
                     ans=self.__result['ans'],
                     error=self.__result['error']
              )
              opsHistory.save()


       def get(self,request ,format=None):


              self.__expression=request.GET.get('expression',['0'])
              self.__result=self.__useCalculator()
              serializer=self.__getSerializedResult()
              self.__saveHistory()
              return JsonResponse(serializer)

       def post(self,request ,format=None):
              
              calculatorPostSerializer=CalculatorPostSerializer(data=request.data)
              if calculatorPostSerializer.is_valid(): 
                     self.__expression=calculatorPostSerializer.data['expression']
                     self.__result=self.__useCalculator()
                     serializer=self.__getSerializedResult()
                     self.__saveHistory()
                     return JsonResponse(serializer)

              return JsonResponse(calculatorPostSerializer.errors)
