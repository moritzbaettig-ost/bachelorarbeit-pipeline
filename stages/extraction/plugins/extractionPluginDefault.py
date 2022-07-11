from typing import Dict
from stages.extraction import ExtractionPluginInterface
from message import IDSHTTPMessage
from type import Type


class Plugin(ExtractionPluginInterface):
    def extract_features(self, message: IDSHTTPMessage, type: Type) -> Dict:
        dictRequest = {}
        # Basic information
        dictRequest['source_address'] = message.source_address
        dictRequest['method'] = message.method
        dictRequest['path'] = message.path
        dictRequest['protocol_version'] = message.protocol_version
        dictRequest['length'] = len(message)


        # Header information
        for entry in message.header:
            dictRequest[entry] = message.header[entry]

        dictRequest['basic_feature_count'] = len(dictRequest.keys())

        # Query
        if type.has_query:
            dictRequest['path_query'] = message.query
            dictRequest['path_feature_count'] = len(message.query.split('&'))
            count_lower=0
            count_upper=0
            count_numeric=0
            count_spaces=0
            count_specialchar=0
            for i in message.query:
                if(i.islower()):
                    count_lower=count_lower+1
                if(i.isupper()):
                    count_upper=count_upper+1
                if(i.isnumeric()):
                    count_numeric=count_numeric+1
                if(i.isspace()):
                    count_spaces=count_spaces+1
                if((48>ord(i)) or (ord(i)>57 and ord(i)<65) or (ord(i)>90 and ord(i)<97)or(ord(i)>122)):
                    count_specialchar=count_specialchar+1
            dictRequest['path_query_lower']=count_lower
            dictRequest['path_query_upper']=count_upper
            dictRequest['path_query_numeric']=count_numeric
            dictRequest['path_query_spaces']=count_spaces
            dictRequest['path_query_specialchar']=count_specialchar

        # Body
        if type.has_body:
            dictRequest['body'] = message.body
            count_lower=0
            count_upper=0
            count_numeric=0
            count_spaces=0
            count_specialchar=0
            for i in message.body:
                if(i.islower()):
                    count_lower=count_lower+1
                if(i.isupper()):
                    count_upper=count_upper+1
                if(i.isnumeric()):
                    count_numeric=count_numeric+1
                if(i.isspace()):
                    count_spaces=count_spaces+1
                if((48>ord(i)) or (ord(i)>57 and ord(i)<65) or (ord(i)>90 and ord(i)<97)or(ord(i)>122)):
                    count_specialchar=count_specialchar+1
            dictRequest['body_lower']=count_lower
            dictRequest['body_upper']=count_upper
            dictRequest['body_numeric']=count_numeric
            dictRequest['body_spaces']=count_spaces
            dictRequest['body_specialchar']=count_specialchar

        return dictRequest
