"""Animation framework for smooth UI transitions."""

import math
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

from imgui_bundle import imgui
from loguru import logger


class EasingFunction(Enum):
    """Easing functions for animations."""

    LINEAR = "linear"
    EASE_IN_QUAD = "ease_in_quad"
    EASE_OUT_QUAD = "ease_out_quad"
    EASE_IN_OUT_QUAD = "ease_in_out_quad"
    EASE_IN_CUBIC = "ease_in_cubic"
    EASE_OUT_CUBIC = "ease_out_cubic"
    EASE_IN_OUT_CUBIC = "ease_in_out_cubic"
    EASE_IN_SINE = "ease_in_sine"
    EASE_OUT_SINE = "ease_out_sine"
    EASE_IN_OUT_SINE = "ease_in_out_sine"
    EASE_IN_EXPO = "ease_in_expo"
    EASE_OUT_EXPO = "ease_out_expo"
    EASE_IN_OUT_EXPO = "ease_in_out_expo"
    BOUNCE = "bounce"
    ELASTIC = "elastic"


class AnimationState(Enum):
    """Animation states."""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"


@dataclass
class Animation:
    """Animation data."""

    name: str
    start_value: float
    end_value: float
    duration: float
    easing: EasingFunction = EasingFunction.LINEAR
    start_time: float = 0.0
    current_value: float = 0.0
    state: AnimationState = AnimationState.IDLE
    loop: bool = False
    reverse: bool = False
    on_complete: Callable | None = None
    on_update: Callable | None = None


def _apply_easing(easing: EasingFunction, t: float) -> float:
    """Apply easing function to normalized time t in [0, 1]."""
    match easing:
        case EasingFunction.LINEAR:
            return t
        case EasingFunction.EASE_IN_QUAD:
            return t * t
        case EasingFunction.EASE_OUT_QUAD:
            return t * (2 - t)
        case EasingFunction.EASE_IN_OUT_QUAD:
            return t * t * (3 - 2 * t)
        case EasingFunction.EASE_IN_CUBIC:
            return t * t * t
        case EasingFunction.EASE_OUT_CUBIC:
            return (t - 1) * (t - 1) * (t - 1) + 1
        case EasingFunction.EASE_IN_OUT_CUBIC:
            return (
                4 * t * t * t
                if t < 0.5
                else 1 + (t - 1) * (2 * (t - 1)) * (2 * (t - 1))
            )
        case EasingFunction.EASE_IN_SINE:
            return 1 - math.cos(t * math.pi / 2)
        case EasingFunction.EASE_OUT_SINE:
            return math.sin(t * math.pi / 2)
        case EasingFunction.EASE_IN_OUT_SINE:
            return -(math.cos(math.pi * t) - 1) / 2
        case EasingFunction.EASE_IN_EXPO:
            return 0.0 if t == 0 else pow(2, 10 * (t - 1))
        case EasingFunction.EASE_OUT_EXPO:
            return 1.0 if t == 1 else 1 - pow(2, -10 * t)
        case EasingFunction.EASE_IN_OUT_EXPO:
            if t == 0 or t == 1:
                return t
            return (
                pow(2, 20 * t - 10) / 2 if t < 0.5 else (2 - pow(2, -20 * t + 10)) / 2
            )
        case EasingFunction.BOUNCE:
            if t < 1 / 2.75:
                return 7.5625 * t * t
            elif t < 2 / 2.75:
                t -= 1.5 / 2.75
                return 7.5625 * t * t + 0.75
            elif t < 2.5 / 2.75:
                t -= 2.25 / 2.75
                return 7.5625 * t * t + 0.9375
            else:
                t -= 2.625 / 2.75
                return 7.5625 * t * t + 0.984375
        case EasingFunction.ELASTIC:
            if t == 0 or t == 1:
                return t
            return pow(2, -10 * t) * math.sin((t - 0.1) * 5 * math.pi) + 1
        case _:
            return t


class AnimationManager:
    """Manager for animations. update() must be called each render frame."""

    def __init__(self) -> None:
        self.animations: dict[str, Animation] = {}
        logger.debug("Initialized AnimationManager")

    def create(
        self,
        name: str,
        start_value: float,
        end_value: float,
        duration: float,
        easing: EasingFunction = EasingFunction.LINEAR,
        loop: bool = False,
        reverse: bool = False,
        on_complete: Callable | None = None,
        on_update: Callable | None = None,
    ) -> Animation:
        """Create a new animation."""
        animation = Animation(
            name=name,
            start_value=start_value,
            end_value=end_value,
            duration=duration,
            easing=easing,
            current_value=start_value,
            loop=loop,
            reverse=reverse,
            on_complete=on_complete,
            on_update=on_update,
        )
        self.animations[name] = animation
        logger.debug(f"Created animation: {name}")
        return animation

    def start(self, name: str) -> bool:
        """Start an animation by name."""
        if name not in self.animations:
            logger.warning(f"Animation not found: {name}")
            return False
        anim = self.animations[name]
        anim.state = AnimationState.RUNNING
        anim.start_time = imgui.get_time()
        anim.current_value = anim.start_value
        return True

    def pause(self, name: str) -> bool:
        """Pause a running animation."""
        if name not in self.animations:
            return False
        self.animations[name].state = AnimationState.PAUSED
        return True

    def resume(self, name: str) -> bool:
        """Resume a paused animation."""
        if name not in self.animations:
            return False
        anim = self.animations[name]
        if anim.state == AnimationState.PAUSED:
            anim.state = AnimationState.RUNNING
            return True
        return False

    def stop(self, name: str) -> bool:
        """Stop an animation, setting it to its end value."""
        if name not in self.animations:
            return False
        anim = self.animations[name]
        anim.state = AnimationState.COMPLETED
        anim.current_value = anim.end_value
        if anim.on_complete:
            anim.on_complete()
        return True

    def update(self) -> None:
        """Advance all running animations. Must be called from the render thread each frame."""
        current_time = imgui.get_time()
        for anim in self.animations.values():
            if anim.state != AnimationState.RUNNING:
                continue
            elapsed = current_time - anim.start_time
            progress = min(elapsed / anim.duration, 1.0)
            eased = _apply_easing(anim.easing, progress)
            anim.current_value = (
                anim.start_value + (anim.end_value - anim.start_value) * eased
            )
            if anim.on_update:
                anim.on_update(anim.current_value)
            if progress >= 1.0:
                if anim.loop:
                    anim.start_time = current_time
                    if anim.reverse:
                        anim.start_value, anim.end_value = (
                            anim.end_value,
                            anim.start_value,
                        )
                else:
                    anim.state = AnimationState.COMPLETED
                    if anim.on_complete:
                        anim.on_complete()

    def get_value(self, name: str) -> float | None:
        """Get current interpolated value of an animation."""
        if name not in self.animations:
            return None
        return self.animations[name].current_value

    def is_running(self, name: str) -> bool:
        """Check if an animation is currently running."""
        if name not in self.animations:
            return False
        return self.animations[name].state == AnimationState.RUNNING

    def remove(self, name: str) -> bool:
        """Remove an animation."""
        if name in self.animations:
            del self.animations[name]
            return True
        return False

    def clear(self) -> None:
        """Remove all animations."""
        self.animations.clear()
