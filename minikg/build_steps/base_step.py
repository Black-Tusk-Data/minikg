import abc
import logging
import os
from pathlib import Path
import time
from typing import Generic, Type, TypeVar


from minikg.models import MiniKgConfig
from minikg.build_output import MiniKgBuildPlanStepOutput

T = TypeVar("T", bound=MiniKgBuildPlanStepOutput)
SLEEP_ON_FAIL_S = 5


def _get_cache_output_path(config: MiniKgConfig, cls, instance_id: str = "") -> Path:
    clsname = cls.__name__
    assert instance_id
    return config.persist_dir / clsname / instance_id


class MiniKgBuilderStep(Generic[T], abc.ABC):
    def __init__(self, config: MiniKgConfig, *, ignore_cache: bool = False):
        self.config = config
        self.executed = False
        self.output: None | T = None
        self.ignore_cache = ignore_cache
        self.cache_bucket = None
        if config.s3_cache_bucket_name:
            from btdcore.aws.s3bucket import S3Bucket

            self.cache_bucket = S3Bucket(bucket_name=config.s3_cache_bucket_name)
        return

    def _get_cache_output_path(self) -> Path:
        return _get_cache_output_path(
            self.config,
            self.__class__,
            self.get_id(),
        )

    def _write_output_to_cache(self):
        output = self.get_output()
        output_path = self._get_cache_output_path()
        os.makedirs(
            os.path.dirname(output_path),
            exist_ok=True,
        )
        with open(output_path, "wb") as f:
            f.write(output.to_bytes())
            pass
        if self.cache_bucket:
            self.cache_bucket.write_to_key(
                key="".join(
                    [
                        self.config.s3_cache_bucket_prefix,
                        str(output_path),
                    ]
                ),
                contents=output.to_bytes(),
            )
            pass
        return

    def _get_cached_output(self) -> T | None:
        cached_output_path = self._get_cache_output_path()
        output_type = self.__class__.get_output_type()

        # first try local fs
        if cached_output_path.exists():
            try:
                with open(cached_output_path, "rb") as f:
                    return output_type.from_bytes(f.read())
                pass
            except Exception as e:
                logging.error(
                    "Failed to load cached KG build step from %s: %s",
                    cached_output_path,
                    e,
                )
                pass
            pass

        if self.cache_bucket:
            s3_key = "".join(
                [
                    self.config.s3_cache_bucket_prefix,
                    str(cached_output_path),
                ]
            )
            if self.cache_bucket.key_exists(s3_key):
                raw = self.cache_bucket.read_at_key(s3_key)
                output = None
                try:
                    output = output_type.from_bytes(raw)
                except Exception as e:
                    logging.error(
                        "Failed to load S3 cached KG build step from %s: %s",
                        cached_output_path,
                        e,
                    )
                    return None
                # # save locally
                # with open(cached_output_path, "wb") as f:
                #     f.write(raw)
                #     pass
                return output
            pass
        return None

    def execute(self) -> None:
        if self.executed:
            this_id = self.get_id()
            raise Exception(f"Step {this_id} has already executed")

        cached_output = self._get_cached_output()
        if not self.ignore_cache and cached_output:
            logging.debug(
                "Using cached %s %s",
                self.__class__.__name__,
                self.get_id(),
            )
            self.output = cached_output
            self.executed = True
            return

        for attempt in range(self.config.max_step_attempts):
            try:
                self.output = self._execute()
                break
            except Exception as e:
                will_retry = attempt + 1 < self.config.max_step_attempts
                logging.exception(
                    "KG build process step %s caught an error %s , will retry? %s",
                    self.__class__.__name__,
                    e,
                    will_retry,
                )
                if not will_retry:
                    raise e
                time.sleep(SLEEP_ON_FAIL_S)
                pass
            pass

        self.executed = True
        self._write_output_to_cache()
        return

    def get_output(self) -> T:
        assert self.executed
        assert self.output != None
        return self.output

    @classmethod
    def load_from_cache(
        cls,
        *,
        config: MiniKgConfig,
        instance_id: str,
    ) -> T:
        cache_path = _get_cache_output_path(
            config,
            cls,
            instance_id,
        )
        output_type = cls.get_output_type()
        if cache_path.exists():
            with open(cache_path, "rb") as f:
                return output_type.from_bytes(f.read())
            pass
        if config.s3_cache_bucket_name:
            from btdcore.aws.s3bucket import S3Bucket

            cache_bucket = S3Bucket(bucket_name=config.s3_cache_bucket_name)
            s3_key = "".join(
                [
                    config.s3_cache_bucket_prefix,
                    str(cache_path),
                ]
            )
            raw = cache_bucket.read_at_key(s3_key)
            return output_type.from_bytes(raw)
        return

    @abc.abstractmethod
    def _execute(self) -> T:
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def get_output_type() -> Type[T]:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_id(self) -> str:
        """
        A unique identifier for caching.
        Note it must only be unique among classes of the same type.
        """
        raise NotImplementedError()

    @classmethod
    def load_from_output(
        cls: type["MiniKgBuilderStep"],
        *,
        output: MiniKgBuildPlanStepOutput,
        config: MiniKgConfig,
    ) -> "MiniKgBuilderStep":
        loaded = cls(config)
        loaded.output = output
        loaded.executed = True
        return loaded

    pass


# # an experiment...
# class MiniKgBuilderExecutedStep(Generic[T], MiniKgBuilderStep[T], abc.ABC):
#     output: T
#     pass
