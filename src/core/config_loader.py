import os


class Config:
    def __init__(self):
        self.repo_path = ""
        self.generate_srd = True


def load_config():
    # src directory
    src_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )

    config_path = os.path.join(src_dir, "config", "config.properties")

    config = Config()

    with open(config_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            if key == "repo.path":
                config.repo_path = value

            elif key == "generate.srd":
                config.generate_srd = value.lower() == "true"

    return config

ROLE_CONFIG = {
    "controller": {
        "folders": ["controller", "controllers", "web", "api"],
        "annotations": ["@RestController", "@Controller"],
    },
    "service": {
        "folders": ["service", "services", "serviceimpl", "impl"],
        "annotations": ["@Service", "@Component","@WebService"],
    },
    "repository": {
        "folders": ["repository", "repositories", "repo", "dao", "persistence"],
        "annotations": ["@Repository"],
        "interfaces": [
            "JpaRepository",
            "CrudRepository",
            "PagingAndSortingRepository"
        ],
    },
    "entity": {
        "folders": ["entity", "entities", "model", "domain"],
        "annotations": ["@Entity", "@Table"],
    },
    "dto": {
        "folders": ["dto", "request", "response", "payload"],
        "annotations": [],
    },
}
