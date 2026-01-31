import json


def print_ir(ir_objects):
    """
    Generic IR printer.
    Converts IR objects to JSON-safe dicts and prints them.
    """

    output = []

    for obj in ir_objects:
        # Case 1: IR object (EndpointIR, etc.)
        if hasattr(obj, "__dict__"):
            output.append(obj.__dict__)

        # Case 2: Already a dict
        elif isinstance(obj, dict):
            output.append(obj)

        else:
            raise TypeError(
                f"Unsupported IR object type: {type(obj)}"
            )

    print(json.dumps(output, indent=2))

    
def print_service_flows(flows):
    serializable = [f.to_dict() for f in flows]
    print(json.dumps(serializable, indent=2))