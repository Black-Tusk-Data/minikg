import os
from pathlib import Path
import subprocess

from minikg.api import Api as MiniKgApi
from minikg.models import MiniKgConfig


GITHUB_CLONE_TO_DIR = Path("./.github")


class KgApiCode:
    def __init__(
        self,
        *,
        ignore_file_exps: list[str],
        input_file_exps: list[str],
        github_url: str = "",
        local_dir: str = "",
    ):
        if not any([github_url, local_dir]):
            raise Exception("expected one of 'github_url' or 'local_dir'")

        self.input_dir = (
            Path(local_dir) if local_dir else self._clone_github_url(github_url)
        )
        self.project_name = os.path.split(self.input_dir.absolute())[-1]

        self.minikgapi = MiniKgApi(
            config=MiniKgConfig(
                community_algorithm="leiden",
                chunk_overlap_lines=2,
                document_desc="code file",
                entity_description_desc="A short description of the code construct",
                entity_name_desc="Qualified name of the entity (include class name if relevant)",
                entity_type_desc="Type of code construct",
                entity_types=[
                    "CLASS",
                    "FUNCTION",
                    "CONSTANT",
                    "CLASS_PROPERTY",
                    "CLASS_METHOD",
                    "TYPE",
                ],
                extraction_prompt_override_entity_head=" ".join(
                    [
                        "Given a code snippet, identify any code constructs that are defined *at the top level of the module*.",
                        "Do not identify any local variables.",
                    ]
                ),
                extraction_prompt_override_entity_relationship_undirected=" ".join(
                    [
                        "Given a code snippet, identify the most meaningful relationships between the given code constructs",
                    ]
                ),
                force_uppercase_node_names=False,
                ignore_expressions=ignore_file_exps,
                index_graph=False,
                input_dir=Path(self.input_dir),
                input_file_exps=input_file_exps,
                knowledge_domain="software code",
                max_concurrency=8,
                max_chunk_lines=300,
                persist_dir=Path(f"./kgcache_{self.project_name}"),
                role_desc="an expert software engineer",
                summary_prompts={
                    "name": "Assign a name to the logical part of a software system that is defined by all sections of the provided context.  Your response should simply be the name of the subsystem.",
                    "purpose": "Describe the purpose of a portion of a software system that is defined by all sections of the provided context.  Your response should be succinct and to-the-point.  Ensure you summarize the CUMULATIVE purpose of each described section combined.",
                },
                version=1,
            ),
        )
        return

    def _clone_github_url(self, github_url: str) -> Path:
        repo_name = github_url.split("/")[-1].split(".git")[0]
        dest_path = GITHUB_CLONE_TO_DIR / repo_name
        if dest_path.exists():
            return dest_path
        os.makedirs(GITHUB_CLONE_TO_DIR, exist_ok=True)
        subprocess.check_call(
            ["git", "clone", github_url, repo_name], cwd=GITHUB_CLONE_TO_DIR.absolute()
        )
        return dest_path

    pass
