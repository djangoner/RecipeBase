from dataclasses import dataclass
from functools import partial
import logging
from typing import Callable, Type, TypeAlias
from django.db.models import Model
from rest_framework.serializers import ModelSerializer
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

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
    deleted: bool = False

    def asdict(self):
        _dict = self.__dict__.copy()
        return _dict


TypeCallback: TypeAlias = Callable[[dict], None]


def model_receiver(sender: Type[Model], instance: Type[Model], model_info: ModelInfo, callback: TypeCallback, **kwargs):
    deleted = kwargs.get("deleted", False)
    created = kwargs.get("created", False)

    model_data = dict(model_info.serializer(instance).data)
    data_model = UpdateData(data=model_data, created=created, deleted=deleted, model=str(sender.__name__))
    data = data_model.asdict()
    data["type"] = "model_update"

    if instance.id is not None and not created and not deleted:
        prev_model = sender.objects.get(id=instance.id)
        is_equal = dict(model_info.serializer(instance).data) == dict(model_info.serializer(prev_model).data)
        if is_equal:
            # log.debug("Skipped model by equal", sender, instance.id)
            return

    # log.debug("Changed model: ", instance.id)

    try:
        callback(data)
    except Exception as e:
        log.error("Callback exception", exc_info=e)


def register_model(model: ModelInfo, callback):
    handler = partial(model_receiver, model_info=model, callback=callback)
    receiver(post_save, sender=model.model)(handler)
    receiver(post_delete, sender=model.model)(partial(handler, deleted=True))


def register_models(models: list[ModelInfo], callback: TypeCallback) -> None:
    for model in models:
        log.info(f"Register model: {model}")
        register_model(model, callback)
