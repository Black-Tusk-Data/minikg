import os
from pathlib import Path
import subprocess

from minikg.api import Api as MiniKgApi
from minikg.build_output import BuildStepOutput_Package
from minikg.models import MiniKgConfig


GITHUB_CLONE_TO_DIR = Path("./.github")


class KgApiCode:
    def build_kg(
        self,
        *,
        github_url: str = "",
        local_dir: str = "",
        ignore_file_exps: list[str],
        input_file_exps: list[str],
    ) -> MiniKgConfig:
        if not any([github_url, local_dir]):
            raise Exception("expected one of 'github_url' or 'local_dir'")
        input_dir = local_dir if local_dir else str(self._clone_github_url(github_url))
        project_name = os.path.split(Path(input_dir).absolute())[-1]
        minikgapi = self._get_minikg_api(
            project_name=project_name,
            ignore_file_exps=ignore_file_exps,
            input_dir=input_dir,
            input_file_exps=input_file_exps,
        )
        minikgapi.build_kg()
        return minikgapi.config

    def load_kg_package(
        self,
        *,
        cache_dir: str,
    ) -> BuildStepOutput_Package:
        minikgapi = self._get_minikg_api(
            cache_dir=cache_dir,
        )
        return minikgapi._load_package()

    def _get_minikg_api(
        self,
        *,
        cache_dir: str = "",
        ignore_file_exps: list[str] | None = None,
        input_dir: str = "",
        input_file_exps: list[str] | None = None,
        project_name: str = "",
    ) -> MiniKgApi:
        return MiniKgApi(
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
                ignore_expressions=ignore_file_exps or [],
                index_graph=False,
                input_dir=Path(input_dir),
                input_file_exps=input_file_exps or [],
                knowledge_domain="software code",
                max_concurrency=8,
                max_chunk_lines=300,
                persist_dir=(
                    Path(cache_dir)
                    if cache_dir
                    else Path(self._get_default_cache_path_name(project_name))
                ),
                role_desc="an expert software engineer",
                summary_prompts={
                    "name": "Assign a name to the logical part of a software system that is defined by all sections of the provided context.  Your response should simply be the name of the subsystem.",
                    "purpose": "Describe the purpose of a portion of a software system that is defined by all sections of the provided context.  Your response should be succinct and to-the-point.  Ensure you summarize the CUMULATIVE purpose of each described section combined.",
                },
                version=1,
            ),
        )
        return

    def _get_default_cache_path_name(self, project_name: str) -> str:
        return f"./kgcache_{project_name}"

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
