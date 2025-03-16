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
    def __init__(self, label: str):
        super().__init__(config, ignore_cache=True)
        self.label = label
        return

    @staticmethod
    def get_output_type() -> type[BuildStepOutput_Text]:
        return BuildStepOutput_Text

    def _execute(self) -> BuildStepOutput_Text:
        text = ":".join([self.__class__.__name__, self.label])
        EXECUTED_STEPS.append(text)
        return BuildStepOutput_Text(text=text)

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
                return [Step_Test1("1")]

            pass

        se = StepExecutor(config)
        se.run_all_coordinators([StepCoordinator_Test1(config=config)])
        self.assertEqual(EXECUTED_STEPS, ["Step_Test1:1"])
        return

    def test_one_coordinator_multiple_steps(self):
        class StepCoordinator_Test1(StepCoordinator):
            def get_required_step_types(self):
                return []

            def get_step_type(self):
                return Step_Test1

            def get_steps_to_execute(self, **kwargs):
                return [Step_Test1("1"), Step_Test1("2"), Step_Test1("3")]

            pass

        se = StepExecutor(config)
        se.run_all_coordinators([StepCoordinator_Test1(config=config)])
        self.assertEqual(
            EXECUTED_STEPS,
            [
                "Step_Test1:1",
                "Step_Test1:2",
                "Step_Test1:3",
            ],
        )
        return

    def test_two_coordinators(self):
        class StepCoordinator_Test1(StepCoordinator):
            def get_required_step_types(self):
                return []

            def get_step_type(self):
                return Step_Test1

            def get_steps_to_execute(self, **kwargs):
                return [
                    Step_Test1("1"),
                    Step_Test1("2"),
                    Step_Test1("3"),
                ]

            pass

        class StepCoordinator_Test2(StepCoordinator):
            def get_required_step_types(self):
                return [Step_Test1]

            def get_step_type(self):
                return Step_Test2

            def get_steps_to_execute(
                self,
                steps_Test1: list[Step_Test1],
                **kwargs,
            ):
                labels = [step.output.text.split(":")[-1] for step in steps_Test1]
                return [Step_Test2(label) for label in labels]

            pass

        se = StepExecutor(config)
        se.run_all_coordinators(
            [
                StepCoordinator_Test1(config=config),
                StepCoordinator_Test2(config=config),
            ]
        )
        self.assertEqual(
            EXECUTED_STEPS,
            [
                "Step_Test1:1",
                "Step_Test1:2",
                "Step_Test1:3",
                "Step_Test2:1",
                "Step_Test2:2",
                "Step_Test2:3",
            ],
        )
        return

    pass


if __name__ == "__main__":
    unittest.main()
