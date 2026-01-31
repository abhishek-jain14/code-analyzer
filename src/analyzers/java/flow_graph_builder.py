import os

from src.analyzers.java.path_utils import normalize_path

def build_business_flows(
    endpoints,
    controller_service_flows,
    service_repository_flows,
    repositories,
    entities,
    service_validations,
    repository_queries
):
    print(">>> BUILD BUSINESS FLOWS INVOKED")

    business_flows = []

    # -------------------------------------------------
    # CONTROLLER → SERVICE (REST ONLY)
    # -------------------------------------------------
    cs_index = {}
    for flow in controller_service_flows:
        key = ("REST", f"{flow.http_method} {flow.path}")
        cs_index[key] = flow
        print(f"🔗 CS FLOW: {key} → {flow.service}.{flow.service_method}")

    # -------------------------------------------------
    # SERVICE → REPOSITORY
    # -------------------------------------------------
    sr_index = {}
    for flow in service_repository_flows:
        key = (flow["service"], flow["service_method"])
        sr_index[key] = flow
        print(
            f"🔗 SR FLOW: {flow['service']}.{flow['service_method']} → "
            f"{flow['repository']}.{flow['repository_method']}"
        )

    # -------------------------------------------------
    # SERVICE → VALIDATIONS
    # -------------------------------------------------
    validation_index = {}
    for v in service_validations:
        key = (v["service"], v["method"])
        validation_index.setdefault(key, []).append(v)

    # -------------------------------------------------
    # ENTITY → TABLE
    # -------------------------------------------------
    entity_table_index = {}
    print("\n>>> ENTITY → TABLE INDEX")
    for e in entities:
        entity_table_index[e["name"]] = e["table"]
        print(f"  {e['name']} → {e['table']}")

    # -------------------------------------------------
    # BUILD FLOWS
    # -------------------------------------------------
    for ep in endpoints:
        print(f"\n➡️ Processing endpoint: {ep.protocol}")

        # -----------------------------
        # REST
        # -----------------------------
        if ep.protocol == "REST":
            method = ep.http_method

            path = ep.path
            print(f"🧼 REST DIRECT SERVICE: {method} {path}")
            #path = path.replace("/api", "")
            #path = "/" + path.strip("/").split("/")[-1]
            key = ("REST", f"{ep.http_method} {ep.path}")
            print(" REST Lookup key:", key)
            cs_flow = cs_index.get(key)

            if not cs_flow:
                print("❌ No Controller→Service flow found")
                continue

            service = cs_flow.service
            service_method = cs_flow.service_method

        # -----------------------------
        # SOAP
        # -----------------------------
        else:
            service = ep.service
            service_method = ep.operation
            print(f"🧼 SOAP DIRECT SERVICE: {service}.{service_method}")

        # -----------------------------
        # SERVICE → REPOSITORY
        # -----------------------------
        repo_flow = sr_index.get((service, service_method))

        if repo_flow:
            
            repository = repo_flow["repository"]
            repo_method = repo_flow["repository_method"]

            entity = repository.replace("Repository", "")
            table = entity_table_index.get(entity)

            query = repository_queries.get(
                (repository, repo_method)
            )
            print(f"🧠 REPO QUERY FOUND: {repository}.{repo_method} → {query}")
            if not query:
                if repo_method.startswith("save"):
                    query = "INSERT"
                elif repo_method.startswith("find"):
                    query = "SELECT"
                elif repo_method.startswith("delete"):
                    query = "DELETE"
                else:
                    query = "UNKNOWN"
        else:
            repository = entity = table = query = None

        validations = validation_index.get(
            (service, service_method), []
        )

        business_flows.append({
            "protocol": ep.protocol,
            "endpoint": ep.path if ep.protocol == "REST" else None,
            "service": f"{service}.{service_method}",
            "repository": repository,
            "entity": entity,
            "table": table,
            "query": query,
            "validations": validations,
            "file": os.path.basename(ep.file)
            #"file": normalize_path(ep.file)
        })

    print(f"\n>>> BUSINESS FLOWS BUILT: {len(business_flows)}")
    return business_flows
