from dataclasses import dataclass, field
from typing import List, Optional

class EndpointIR:
    def __init__(
        self,
        http_method=None,
        path=None,
        handler=None,
        file=None,
        protocol="REST",
        operation=None,
        service=None
    ):
        self.http_method = http_method
        self.path = path
        self.handler = handler
        self.file = file
        self.protocol = protocol
        self.operation = operation
        self.service = service

    def to_dict(self):
        return {
            "protocol": self.protocol,
            "http_method": self.http_method,
            "path": self.path,
            "service": self.service,
            "operation": self.operation or self.handler,
            "file": self.file,
        }
       



class ServiceFlowIR:
    def __init__(self, service, method, file):
        self.service = service
        self.method = method
        self.file = file

    def to_dict(self):
        return {
            "service": self.service,
            "method": self.method,
            "file": self.file
        }

class ControllerServiceFlowIR:
    def __init__(self, endpoint, controller, service, service_method,  http_method=None, path=None, inputs=None):
        self.endpoint = endpoint
        self.controller = controller
        self.service = service
        self.service_method = service_method
        self.http_method = http_method
        self.path = path
        self.inputs = inputs or []

    def to_dict(self):
        return {
            "endpoint": self.endpoint,
            "controller": self.controller,
            "service": self.service,
            "service_method": self.service_method,
            "http_method": self.http_method,
            "path": self.path,
            "inputs": self.inputs
        }

class EntityFieldIR:
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type
        }


class EntityIR:
    def __init__(self, name, table, fields):
        self.name = name
        self.table = table
        self.fields = fields  # list[EntityFieldIR]

    def to_dict(self):
        return {
            "name": self.name,
            "table": self.table,
            "fields": [f.to_dict() for f in self.fields]
        }


class RepositoryIR:
    def __init__(self, name, entity, queries):
        self.name = name
        self.entity = entity
        self.queries = queries

    def to_dict(self):
        return {
            "repository": self.name,
            "entity": self.entity,
            "queries": self.queries
        }

class BusinessFlowIR:
    def __init__(
        self,
        endpoint,
        http_method,
        controller,
        service=None,
        service_method=None,
        repository=None,
        repository_method=None,
        entity=None,
        table=None,
        fields=None,
    ):
        self.endpoint = endpoint
        self.http_method = http_method
        self.controller = controller
        self.service = service
        self.service_method = service_method
        self.repository = repository
        self.repository_method = repository_method
        self.entity = entity
        self.table = table
        self.fields = fields or []

    def to_dict(self):
        return {
            "endpoint": self.endpoint,
            "http_method": self.http_method,
            "controller": self.controller,
            "service": self.service,
            "service_method": self.service_method,
            "repository": self.repository,
            "repository_method": self.repository_method,
            "entity": self.entity,
            "table": self.table,
            "fields": self.fields,
        }

class ServiceRepositoryFlowIR:
    def __init__(self, service, service_method, repository, repository_method, file):
        self.service = service
        self.service_method = service_method
        self.repository = repository
        self.repository_method = repository_method
        self.file = file

    def to_dict(self):
        return {
            "service": self.service,
            "service_method": self.service_method,
            "repository": self.repository,
            "repository_method": self.repository_method,
            "file": self.file,
        }
