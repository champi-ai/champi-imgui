"""Tests for AnimationManager and EasingFunction."""

from unittest.mock import patch

import pytest

from champi_imgui.extensions.animation import (
    AnimationManager,
    AnimationState,
    EasingFunction,
    _apply_easing,
)


class TestEasingFunction:
    def test_linear(self) -> None:
        assert _apply_easing(EasingFunction.LINEAR, 0.5) == pytest.approx(0.5)

    def test_linear_boundaries(self) -> None:
        assert _apply_easing(EasingFunction.LINEAR, 0.0) == 0.0
        assert _apply_easing(EasingFunction.LINEAR, 1.0) == 1.0

    def test_ease_in_quad(self) -> None:
        v = _apply_easing(EasingFunction.EASE_IN_QUAD, 0.5)
        assert v == pytest.approx(0.25)

    def test_ease_out_quad(self) -> None:
        v = _apply_easing(EasingFunction.EASE_OUT_QUAD, 0.5)
        assert v == pytest.approx(0.75)

    def test_ease_in_expo_at_zero(self) -> None:
        assert _apply_easing(EasingFunction.EASE_IN_EXPO, 0.0) == 0.0

    def test_ease_out_expo_at_one(self) -> None:
        assert _apply_easing(EasingFunction.EASE_OUT_EXPO, 1.0) == 1.0

    def test_bounce_start(self) -> None:
        v = _apply_easing(EasingFunction.BOUNCE, 0.0)
        assert v == pytest.approx(0.0)

    def test_elastic_boundaries(self) -> None:
        assert _apply_easing(EasingFunction.ELASTIC, 0.0) == 0.0
        assert _apply_easing(EasingFunction.ELASTIC, 1.0) == 1.0

    def test_all_easing_values_run(self) -> None:
        for ef in EasingFunction:
            result = _apply_easing(ef, 0.5)
            assert isinstance(result, float)


class TestAnimationManager:
    def test_create(self) -> None:
        manager = AnimationManager()
        anim = manager.create("test", 0.0, 100.0, 1.0)
        assert "test" in manager.animations
        assert anim.start_value == 0.0
        assert anim.end_value == 100.0
        assert anim.duration == 1.0

    def test_create_with_easing(self) -> None:
        manager = AnimationManager()
        anim = manager.create("anim", 0, 1, 0.5, easing=EasingFunction.EASE_OUT_QUAD)
        assert anim.easing == EasingFunction.EASE_OUT_QUAD

    def test_start_not_found(self) -> None:
        manager = AnimationManager()
        assert manager.start("ghost") is False

    def test_start_sets_running(self) -> None:
        manager = AnimationManager()
        manager.create("a", 0, 1, 1.0)
        with patch("champi_imgui.extensions.animation.imgui") as mock_imgui:
            mock_imgui.get_time.return_value = 0.0
            result = manager.start("a")
        assert result is True
        assert manager.animations["a"].state == AnimationState.RUNNING

    def test_stop_not_found(self) -> None:
        manager = AnimationManager()
        assert manager.stop("ghost") is False

    def test_stop_sets_end_value(self) -> None:
        manager = AnimationManager()
        manager.create("a", 0, 100, 1.0)
        with patch("champi_imgui.extensions.animation.imgui") as mock_imgui:
            mock_imgui.get_time.return_value = 0.0
            manager.start("a")
        manager.stop("a")
        assert manager.animations["a"].current_value == 100.0
        assert manager.animations["a"].state == AnimationState.COMPLETED

    def test_stop_calls_on_complete(self) -> None:
        manager = AnimationManager()
        called = []
        manager.create("a", 0, 1, 1.0, on_complete=lambda: called.append(True))
        manager.stop("a")
        assert called == [True]

    def test_pause_resume(self) -> None:
        manager = AnimationManager()
        manager.create("a", 0, 1, 1.0)
        with patch("champi_imgui.extensions.animation.imgui") as mock_imgui:
            mock_imgui.get_time.return_value = 0.0
            manager.start("a")
        manager.pause("a")
        assert manager.animations["a"].state == AnimationState.PAUSED
        manager.resume("a")
        assert manager.animations["a"].state == AnimationState.RUNNING

    def test_get_value_not_found(self) -> None:
        manager = AnimationManager()
        assert manager.get_value("ghost") is None

    def test_get_value_initial(self) -> None:
        manager = AnimationManager()
        manager.create("a", 10.0, 20.0, 1.0)
        assert manager.get_value("a") == 10.0

    def test_is_running(self) -> None:
        manager = AnimationManager()
        manager.create("a", 0, 1, 1.0)
        assert manager.is_running("a") is False
        with patch("champi_imgui.extensions.animation.imgui") as mock_imgui:
            mock_imgui.get_time.return_value = 0.0
            manager.start("a")
        assert manager.is_running("a") is True

    def test_is_running_not_found(self) -> None:
        manager = AnimationManager()
        assert manager.is_running("ghost") is False

    def test_remove(self) -> None:
        manager = AnimationManager()
        manager.create("a", 0, 1, 1.0)
        assert manager.remove("a") is True
        assert "a" not in manager.animations

    def test_remove_not_found(self) -> None:
        manager = AnimationManager()
        assert manager.remove("ghost") is False

    def test_clear(self) -> None:
        manager = AnimationManager()
        manager.create("a", 0, 1, 1.0)
        manager.create("b", 0, 1, 1.0)
        manager.clear()
        assert manager.animations == {}

    def test_update_advances_value(self) -> None:
        manager = AnimationManager()
        manager.create("a", 0.0, 100.0, 2.0)
        with patch("champi_imgui.extensions.animation.imgui") as mock_imgui:
            mock_imgui.get_time.return_value = 0.0
            manager.start("a")
            # Advance to halfway
            mock_imgui.get_time.return_value = 1.0
            manager.update()
        assert manager.animations["a"].current_value == pytest.approx(50.0)

    def test_update_completes_animation(self) -> None:
        manager = AnimationManager()
        manager.create("a", 0.0, 100.0, 1.0)
        with patch("champi_imgui.extensions.animation.imgui") as mock_imgui:
            mock_imgui.get_time.return_value = 0.0
            manager.start("a")
            # Past end time
            mock_imgui.get_time.return_value = 2.0
            manager.update()
        assert manager.animations["a"].state == AnimationState.COMPLETED

    def test_update_calls_on_update_callback(self) -> None:
        manager = AnimationManager()
        values = []
        manager.create("a", 0.0, 100.0, 1.0, on_update=values.append)
        with patch("champi_imgui.extensions.animation.imgui") as mock_imgui:
            mock_imgui.get_time.return_value = 0.0
            manager.start("a")
            mock_imgui.get_time.return_value = 0.5
            manager.update()
        assert len(values) == 1
