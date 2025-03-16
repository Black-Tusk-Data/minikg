from pathlib import Path
import unittest

from minikg.build_output import BuildStepOutput_Text
from minikg.build_steps.base_step import MiniKgBuilderStep
from minikg.models import MiniKgConfig
from minikg.step_coordinators.base import StepCoordinator
from minikg.step_executor import StepExecutor


EXECUTED_STEPS = []


config = MiniKgConfig(
    version=1,
    knowledge_domain="test",
    entity_types=[],
    persist_dir=Path("/tmp"),
    input_dir=Path("/tmp"),
    input_file_exp="*",
    max_chunk_lines=10,
    chunk_overlap_lines=1,
)


class BaseTestStep(MiniKgBuilderStep[BuildStepOutput_Text]):
    @staticmethod
    def get_output_type() -> type[BuildStepOutput_Text]:
        return BuildStepOutput_Text

    def _execute(self) -> BuildStepOutput_Text:
        EXECUTED_STEPS.append(self.__class__.__name__)
        return BuildStepOutput_Text(text=self.__class__.__name__)

    def get_id(self):
        return "id-test"

    pass


class Step_Test1(BaseTestStep):
    pass


class Step_Test2(BaseTestStep):
    pass


class Step_Test3(BaseTestStep):
    pass


class Test_StepExecutor(unittest.TestCase):
    # TODO: need to 'before each' set the executed steps to []
    def test_one_coordinator_one_step(self):
        class StepCoordinator_Test1(StepCoordinator):
            def get_required_step_types(self):
                return []

            def get_step_type(self):
                return Step_Test1

            def get_steps_to_execute(self, **kwargs):
                return [Step_Test1(config=self.config, ignore_cache=True)]

            pass

        se = StepExecutor(config)
        se.run_all_coordinators([StepCoordinator_Test1(config=config)])
        self.assertEqual(EXECUTED_STEPS, ["Step_Test1"])
        return

    pass


if __name__ == "__main__":
    unittest.main()
