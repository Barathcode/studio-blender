"""Background task that is invoked after every frame change and that handles
tethers of drones and related safety checks in the current frame.
"""

import bpy

from typing import List

from sbstudio.model.types import Coordinate3D
from sbstudio.plugin.constants import Collections

from .base import Task
from sbstudio.plugin.utils.evaluator import get_position_of_object


def get_position_of_objects_in_collection(collection) -> List[Coordinate3D]:
    """Retrieves the current position of objects in the given collection in the
    order they appear in the collection.
    """
    return [get_position_of_object(object) for object in collection.objects]


def run_tethers(scene, depsgraph):

    tethers = scene.skybrush.tethers
    settings = scene.skybrush.settings
    safety_check = scene.skybrush.safety_check

    if not tethers or not settings or not safety_check:
        return

    if settings.use_tethered_drones:
        drones = Collections.find_drones(create=False)
        first_formation = scene.skybrush.storyboard.first_formation
    else:
        drones = None
        first_formation = None

    if not drones or not first_formation:
        tethers.clear_tethers()
        return

    # get home and current positions
    # Note that we retrieve home positions from the first formation, assuming
    # implicitely that it is the takeoff grid and that its position do not
    # change over time. We do this so that we do not need to change frames.
    # This method might be buggy in some corner cases; if that comes up as an
    # issue, a better method will be needed.
    home_positions = get_position_of_objects_in_collection(first_formation)
    positions = get_position_of_objects_in_collection(drones)

    # perform safety checks
    min_distance = 0
    max_length = 0
    tethers_over_max_length = []
    if safety_check.enabled:
        # perform tether length safety checks
        if tethers.length_warning_enabled:
            lengths = [
                ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5
                for a, b in zip(home_positions, positions)
            ]
            max_length = max(lengths)
            tethers_over_max_length = [
                ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2)
                for a, b, length in zip(home_positions, positions, lengths)
                if length > tethers.length_warning_threshold
            ]

        # perform tether distance safety check
        # TODO

    tethers.update_tethers_and_safety_check_result(
        tethers=[[a, b] for a, b in zip(home_positions, positions)],
        min_distance=min_distance,
        max_length=max_length,
        tethers_over_max_length=tethers_over_max_length,
    )


def ensure_overlays_enabled():
    """Ensures that the tether overlay is enabled after loading a file."""
    tethers = bpy.context.scene.skybrush.tethers
    tethers.ensure_overlays_enabled_if_needed()


def run_tasks_post_load(*args):
    """Runs all the tasks that should be completed after loading a file."""
    ensure_overlays_enabled()


class UpdateTethersTask(Task):
    """Background task that is invoked after every frame change and that
    updates coordinates of tethers and tether-specific safety checks results.
    """

    functions = {
        "depsgraph_update_post": run_tethers,
        "frame_change_post": run_tethers,
        "load_post": run_tasks_post_load,
    }
