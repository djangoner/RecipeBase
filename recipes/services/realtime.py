from dataclasses import dataclass
from functools import partial
import logging
from typing import Callable, Type, TypeAlias
from django.db.models import Model
from rest_framework.serializers import ModelSerializer
from django.dispatch import receiver
from django.db.models.signals import post_save

log = logging.getLogger("Realtime")


@dataclass
class ModelInfo:
    model: Type[Model]
    serializer: Type[ModelSerializer]


@dataclass
class UpdateData:
    model: str
    data: dict
    created: bool = False

    def asdict(self):
        _dict = self.__dict__.copy()
        return _dict


TypeCallback: TypeAlias = Callable[[dict], None]


def model_receiver(sender: Type[Model], instance: Type[Model], model_info: ModelInfo, callback: TypeCallback, **kwargs):
    model_data = dict(model_info.serializer(instance).data)
    data_model = UpdateData(data=model_data, created=kwargs.get("created", False), model=str(sender.__name__))
    data = data_model.asdict()
    data["type"] = "model_update"

    callback(data)


def register_model(model: ModelInfo, callback):
    handler = partial(model_receiver, model_info=model, callback=callback)
    receiver(post_save, sender=model.model)(handler)


def register_models(models: list[ModelInfo], callback: TypeCallback) -> None:
    for model in models:
        log.info(f"Register model: {model}")
        register_model(model, callback)
