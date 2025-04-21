"""
Can cache some of the itermediate state moving forwards
"""

import itertools as it
import logging
from pathlib import Path
import time

from btdcore.utils import batched

from minikg.extractor.entity_relationship_extractor_undirected import (
    EntityRelationshipExtractorUndirected,
)
from minikg.services import services
from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.models import (
    Entity,
    EntityRelationship,
    EntityRelationshipUndirected,
    EntityWithFragment,
    FileFragment,
    MiniKgConfig,
)
from minikg.build_output import BuildStepOutput_Edges
from minikg.splitter import Splitter


class Step_IdentifyEdges(MiniKgBuilderStep[BuildStepOutput_Edges]):
    DELIMITER = "::"
    MAX_FILE_CHARS_FOR_IMPORT_CHECKS = 3000
    MAX_IMPORT_NAMES_PER_STRUCTURED_CHECK = 50
    MAX_IMPORT_NAMES_PER_UNSTRUCTURED_CHECK = 50
    TOO_MANY_ACCESSIBLE_ENTITIES = 200
    TOO_MANY_POTENTIAL_IMPORTS = 201

    MAX_ATTEMPTS = 2
    SLEEP_S = 5

    file_contents: str

    def __init__(
        self,
        config: MiniKgConfig,
        *,
        file_path: Path,
        entities_by_file_path: dict[Path, list[EntityWithFragment]],
    ) -> None:
        super().__init__(config)
        self.entities_by_file_path = entities_by_file_path
        self.file_path = file_path
        self.splitter = Splitter(config=config)
        self.all_entity_names: dict[str, EntityWithFragment] = {
            entity.name.upper(): entity
            for entities in entities_by_file_path.values()
            for entity in entities
        }
        with open(self.config.input_dir / file_path, "r") as f:
            self.file_contents = f.read()
            pass
        return

    def get_id(self) -> str:
        return str(self.file_path).replace("/", ":")

    @staticmethod
    def get_output_type():
        return BuildStepOutput_Edges

    def _identify_imported_paths(
        self, potential_imports: list[EntityWithFragment]
    ) -> list[Path]:
        all_paths: list[str] = list(
            set(entity.fragment.source_path for entity in potential_imports)
        )

        imported_paths: list[Path] = []
        for path_batch in batched(
            all_paths, self.MAX_IMPORT_NAMES_PER_STRUCTURED_CHECK
        ):
            schema = {
                "type": "object",
                "description": "Object indicating which paths are imported",
                "properties": {
                    path: {
                        "type": "boolean",
                    }
                    for path in path_batch
                },
            }
            r = services.llm_api.completion(
                req_name="identify-imported-paths-v3",
                system=" ".join(
                    [
                        f"You are {self.config.role_desc}.",
                        "Given a code file's contents, indicate which file paths that file imports.",
                        "Keep in mind that the code file itself is defined at the path",
                        str(self.file_path),
                    ]
                ),
                user=self.file_contents[: self.MAX_FILE_CHARS_FOR_IMPORT_CHECKS],
                output_schema=schema,
            )
            assert r.structured_output is not None
            imported_paths.extend(
                [
                    Path(key)
                    for key, is_imported in r.structured_output.items()
                    if is_imported
                ]
            )
            pass

        return imported_paths

    def _identify_imported_entities(
        self, *, potential_imports: list[EntityWithFragment]
    ) -> list[EntityWithFragment]:
        by_name = {
            construct.get_qualified_name(): construct for construct in potential_imports
        }

        actual_imports: list[EntityWithFragment] = []
        for name_batch in batched(
            list(by_name.keys()), self.MAX_IMPORT_NAMES_PER_STRUCTURED_CHECK
        ):
            schema = {
                "type": "object",
                "description": f"Object indicating which code constructs are imported",
                "properties": {
                    name: {
                        "type": "boolean",
                    }
                    for name in name_batch
                },
            }
            r = services.llm_api.completion(
                req_name="identify-imported-entities-v3",
                system=" ".join(
                    [
                        f"You are {self.config.role_desc}.",
                        "Given a code file's contents, indicate which code constructs that file imports.",
                        "Keep in mind that the code file itself is defined at the path",
                        str(self.file_path),
                    ]
                ),
                user=self.file_contents[: self.MAX_FILE_CHARS_FOR_IMPORT_CHECKS],
                output_schema=schema,
            )
            assert r.structured_output is not None
            actual_imports.extend(
                [
                    by_name[name]
                    for name, is_imported in r.structured_output.items()
                    if is_imported
                ]
            )
            pass
        return actual_imports

    def _identify_imported_symbols(self) -> list[str]:
        schema = {
            "type": "object",
            "description": f"Object indicating what symbols are imported into a code module",
            "properties": {
                "imported_symbols": {
                    "description": "Any symbols imported by the code module",
                    "type": "array",
                    "items": {
                        "description": "Name of imported symbol",
                        "type": "string",
                    },
                },
            },
        }
        r = services.llm_api.completion(
            req_name="identify-imported-symbols",
            system=" ".join(
                [
                    f"You are {self.config.role_desc}.",
                    "Given a code file's contents, indicate what symbols are imported by that code file.",
                ]
            ),
            user=self.file_contents[: self.MAX_FILE_CHARS_FOR_IMPORT_CHECKS],
            output_schema=schema,
        )
        assert r.structured_output is not None
        return r.structured_output["imported_symbols"]

    def _execute(self):
        logging.info("identifying edges for %s", self.file_path)
        imported_symbols = self._identify_imported_symbols()
        logging.info(
            "determined module %s to import %d symbols",
            self.file_path,
            len(imported_symbols),
        )
        upcase_symbol_names = [sym.upper() for sym in imported_symbols]

        potential_imports: list[EntityWithFragment] = [
            entity
            for upcase_name, entity in self.all_entity_names.items()
            if any(sym in upcase_name for sym in upcase_symbol_names)
        ]
        logging.info(
            "determined module %s to have %d potential construct imports",
            self.file_path,
            len(potential_imports),
        )
        if len(potential_imports) >= self.TOO_MANY_POTENTIAL_IMPORTS:
            imported_paths: set[Path] = set(
                self._identify_imported_paths(potential_imports)
            )
            potential_imports = [
                entity
                for entity in potential_imports
                if Path(entity.fragment.source_path) in imported_paths
            ]
            logging.info(
                "module %s reduced number of potential construct imports to %s",
                self.file_path,
                len(potential_imports),
            )
            pass
        all_accessible_entities = self._identify_imported_entities(
            potential_imports=potential_imports
        )
        logging.info(
            "determined module %s to have %d actual construct imports",
            self.file_path,
            len(all_accessible_entities),
        )

        edges: list[EntityRelationshipUndirected] = []
        # as an efficiency step, could do many entities in a single fragment at once instead
        fragments_by_id: dict[str, FileFragment] = {}
        entities_by_fragment_id: dict[str, list[EntityWithFragment]] = {}
        for entity in self.entities_by_file_path[self.file_path]:
            fragments_by_id[entity.fragment.fragment_id] = entity.fragment
            if entity.fragment.fragment_id not in entities_by_fragment_id:
                entities_by_fragment_id[entity.fragment.fragment_id] = []
                pass
            entities_by_fragment_id[entity.fragment.fragment_id].append(entity)
            pass

        logging.info(
            "identifying relationships to %d fragments for path %s, into %d defined locally-defined entities from %d global entities",
            len(fragments_by_id),
            self.file_path,
            len(self.entities_by_file_path[self.file_path]),
            len(all_accessible_entities),
        )
        for fragment_id in fragments_by_id.keys():
            # TODO:
            # Note that we are missing the potential for some relationships
            # that would have happened across batches.
            for tail_entity_batch in batched(
                entities_by_fragment_id[fragment_id],
                self.MAX_IMPORT_NAMES_PER_STRUCTURED_CHECK,
            ):
                for head_entity_batch in batched(
                    all_accessible_entities, self.MAX_IMPORT_NAMES_PER_STRUCTURED_CHECK
                ):
                    # might need to upper-bound how many things we actually look at here
                    extractor = EntityRelationshipExtractorUndirected(
                        config=self.config,
                        fragment=fragments_by_id[fragment_id],
                        entities=[
                            *head_entity_batch,
                            *tail_entity_batch,
                        ],
                    )
                    edges.extend(extractor.extract())
                    pass
            pass

        # It's OK to just track the edges in one direction,
        # since we usually use Leiden and remove the directionality anyways.
        # TODO: handle an undirected graph here conditionally
        directed_edges: list[EntityRelationship] = []
        for edge in edges:
            for related_entity_pair in it.combinations(edge.related_entities, 2):
                if related_entity_pair[0] == related_entity_pair[1]:
                    continue
                directed_edges.append(
                    EntityRelationship(
                        source_entity=related_entity_pair[0],
                        target_entity=related_entity_pair[1],
                        relationship_description=edge.relationship_description,
                    )
                )
                pass
            pass
        return BuildStepOutput_Edges(edges=directed_edges)

    pass
