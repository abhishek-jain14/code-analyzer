import json

from src.core.config_loader import load_config
from src.core.repo_scanner import scan_repo
from src.analyzers.java.spring_extractor import extract_spring_endpoints
from src.ir.serializer import print_ir
#from src.srd.generator import generate_srd
from src.analyzers.java.service_extractor import extract_service_flows
from src.ir.serializer import print_service_flows
from src.analyzers.java.flow_extractor import extract_controller_service_flows
from src.analyzers.java.repository_extractor import extract_repositories
from src.analyzers.java.flow_graph_builder import build_business_flows
from src.analyzers.java.service_repository_extractor import extract_service_repository_flows
from src.analyzers.java.entity_extractor import extract_entities
from src.analyzers.java.service_validation_extractor import extract_service_validations
from src.analyzers.java.soap_extractor import extract_soap_endpoints
from src.analyzers.java.repository_query_extractor import extract_repository_queries
from src.analyzers.java.entity_extractor import extract_entity_fields
from src.analyzers.java.dto_extractor import extract_controller_inputs
from src.analyzers.java.dto_extractor import extract_input_object_fields



def main():
    global json
    print("DEBUG json type in main:", type(json))
    config = load_config()

    java_files = scan_repo(config.repo_path)
    print("DEBUG java_files[0]:", java_files[0])
    print("DEBUG type:", type(java_files[0]))
    print(">>> JAVA FILES SCANNED:", len(java_files))

    endpoints_ir = extract_spring_endpoints(java_files)
    print(">>> JAVA FILES SCANNED:", len(java_files))

    
    # TEMP test
    soap_endpoints = extract_soap_endpoints(java_files)

    print("\n=== SOAP ENDPOINTS ===")
    #import json
    print(json.dumps([e.to_dict() for e in soap_endpoints], indent=2))


    endpoints_ir.extend(soap_endpoints)


    print("=== IR (JSON) ===")
    print_ir(endpoints_ir)

   # -------- Service Flow Extraction --------
    services = extract_service_flows(java_files)

    #print("\n=== SERVICE FLOWS ===")
    #print_service_flows(services)
    #print(">>> SERVICES EXTRACTED:", len(services))

    service_validations = extract_service_validations(java_files)

    print("\n=== SERVICE VALIDATIONS ===")
    print(json.dumps(service_validations, indent=2))


    #print(">>> FLOW EXTRACTOR RETURNED")
    #print(">>> FLOW COUNT:", len(controller_service_flows))

    #print("\n=== CONTROLLER → SERVICE FLOWS ===")
    #print(json.dumps([f.to_dict() for f in controller_service_flows], indent=2))

    #if config.generate_srd:
      #  print("\n=== SRD ===")
      #  generate_srd(endpoints_ir)

    # -------- Repository / DB Extraction --------
    #print(type(java_files[0]), java_files[0])
    repositories = extract_repositories(java_files)

    #print("\n=== REPOSITORIES ===")
    #print(repositories)

    #print("\n=== REPOSITORIES ===")
    #print(json.dumps(repositories, indent=2))

    entities = extract_entities(java_files)
#    print("\n>>> ENTITIES EXTRACTED:", len(entities))
#    print("\n=== ENTITIES ===", entities)
    entity_fields = extract_entity_fields(entities)
#    print("\n>>> ENTITY FIELDS EXTRACTED:", len(entity_fields))
#    print("\n=== ENTITY FIELDS ===", entity_fields)
    entity_map = {}

    for entity in entities:
        name = entity["name"]
        entity_map[name] = {
            "table": entity.get("table"),
            "fields": entity_fields.get(name, [])
        }
#    print("\n>>> ENTITY MAP BUILT:", len(entity_map))
#    print("\n=== ENTITY MAP ===", entity_map)


    controller_inputs = extract_controller_inputs(java_files)
    print("\n>>> CONTROLLER INPUTS EXTRACTED:", len(controller_inputs))
    print("\n=== CONTROLLER INPUTS ===", controller_inputs)
    input_objects = extract_input_object_fields(java_files, controller_inputs)
    print("\n>>> INPUT OBJECT FIELDS EXTRACTED:", len(input_objects))
    print("\n=== INPUT OBJECT FIELDS ===", input_objects)


  
    #print(">>> CALLING FLOW EXTRACTOR")
    controller_service_flows = extract_controller_service_flows(
        java_files, controller_inputs
    )


    #print("\n=== ENTITIES ===")
    #print(json.dumps(entities, indent=2))

    from src.analyzers.java.service_repository_extractor import (
        extract_service_repository_flows
    )

    service_repository_flows = extract_service_repository_flows(java_files, repositories)

    #print("\n=== SERVICE → REPOSITORY CALLS ===")
    #print(json.dumps(service_repository_flows, indent=2))

    repository_queries = extract_repository_queries(java_files)

    # ---- BUILD END-TO-END FLOWS ----
    business_graph_flows = build_business_flows(
    endpoints=endpoints_ir,
    controller_service_flows=controller_service_flows,
    service_repository_flows=service_repository_flows,
    repositories=repositories,
    entities=entities,
    service_validations=service_validations,
    repository_queries=repository_queries
    )

    output = {
        "flows": [flow.to_dict() for flow in controller_service_flows],
        "entities": entity_map,
        "input_objects": input_objects
    }

    print(json.dumps(output, indent=2))


    #print("\n=== END-TO-END BUSINESS FLOWS ===")
    #print(json.dumps(business_graph_flows, indent=2))


if __name__ == "__main__":
    main()


