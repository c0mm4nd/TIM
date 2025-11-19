# a framework for describing intents
from typing import TypedDict


class Intent(TypedDict):
    scenerio: str
    description: str


def define_intent(scenerio: str, description: str) -> Intent:
    return {"scenerio": scenerio, "description": description}
