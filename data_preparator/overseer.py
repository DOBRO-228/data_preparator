#!/usr/bin/env python3

"""Надзиратель."""
import copy
import time

from .data_preparator import process_data_frame

data_frames_to_prepare = []


def oversee(time_delay):
    """
    Если в список добавились дата фреймы, то предобрабатывает их и добавляет в список с предобработанными дата фреймами.
    """
    while True:
        time.sleep(int(time_delay))
        copy_of_data_frames_to_prepare = copy.deepcopy(data_frames_to_prepare)
        data_frames_to_prepare.clear()
        for new_data_frame in copy_of_data_frames_to_prepare:
            prepared_data_frames.append(process_data_frame(new_data_frame))


prepared_data_frames = []
