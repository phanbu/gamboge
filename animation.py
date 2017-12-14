import pygame


class AnimationSequence:
    def __init__(self, frames, timing, loop=False):
        self.started = None
        self.frames = frames
        self.looping = loop
        if isinstance(timing, int):
            timing = _evenly_distribute(timing, len(frames))
        elif len(frames) != len(timing):
            raise ValueError()
        self.transitions = _compute_frame_transition_times()

    def play(self):
        self.started = pygame.time.get_ticks()

    def stop(self):
        self.started = None

    def get_frame(self):
        pass




def _evenly_distribute(total_time, elements):
    result = []
    frame_length = total_time // elements
    remainder = total_time % elements
    for i in range(elements):
        result.append(frame_length + (1 if i < remainder else 0))
    return result


def _compute_frame_transition_times(timing):
    elapsed_time = 0
    result = [elapsed_time]
    for i in timing:
        elapsed_time += i
        result.append(elapsed_time)
    return result