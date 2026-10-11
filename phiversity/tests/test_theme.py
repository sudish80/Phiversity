import pytest

import numpy as np

from phiversity.theme import (DEFAULT_PRESET, PRESETS, contrast_ratio,
                               kit_source, normalize_preset,
                               relative_luminance, roles, validate_preset)


class TestPresets:
    @pytest.mark.parametrize("preset", sorted(PRESETS))
    def test_contrast_and_distinctness(self, preset):
        assert validate_preset(preset) == []

    @pytest.mark.parametrize("alias,expected", [
        ("auto", DEFAULT_PRESET), ("", DEFAULT_PRESET),
        ("MATH", "math"), ("mathematical", "math"),
        ("lab", "lab"), ("laboratory", "lab"),
        ("spatial", "spatial"), ("3d", "spatial"),
        ("data", "data"), ("charts", "data"),
        ("paper", "paper"), ("light", "paper"), ("notebook", "paper"),
        ("bogus", DEFAULT_PRESET),
    ])
    def test_aliases(self, alias, expected):
        assert normalize_preset(alias) == expected

    def test_paper_is_light_math_is_dark(self):
        assert relative_luminance(roles("paper")["background_primary"]) > 0.8
        assert relative_luminance(roles("math")["background_primary"]) < 0.1

    def test_semantic_roles_resolve(self):
        palette = roles("math")
        assert palette["variable"] == "#65A9FF"
        assert palette["result_final"] == "#75D6A0"
        assert palette["vector_force"] == "#FF6B78"
        assert palette["atom_oxygen"] == "#FF6B78"

    def test_light_theme_swaps_text_roles(self):
        dark, light = roles("math"), roles("paper")
        assert contrast_ratio(light["text_primary"],
                              light["background_primary"]) > 4.5
        assert dark["text_primary"] != light["text_primary"]

    def test_curve_roles_are_distinct(self):
        palette = roles("math")
        curve_roles = ["graph_function", "graph_secant", "graph_tangent",
                       "graph_point", "graph_reference"]
        colors = [palette[r] for r in curve_roles]
        assert len(set(colors)) == len(colors)

    def test_contrast_ratio_bounds(self):
        assert contrast_ratio("#000000", "#FFFFFF") == pytest.approx(21.0,
                                                                    abs=0.1)
        assert contrast_ratio("#FFFFFF", "#FFFFFF") == pytest.approx(1.0)


class TestKitSource:
    def test_kit_compiles_and_carries_preset(self):
        for preset in ("math", "paper", "spatial"):
            source = kit_source(preset)
            compile(source, f"kit_{preset}", "exec")
            bg = roles(preset)["background_primary"]
            assert f'config.background_color = "{bg}"' in source

    @pytest.mark.parametrize("helper", [
        "def zoom_to(", "def pan_to(", "def camera_reset(",
        "def follow(", "def unfollow(", "def orbit_start(",
        "def zoom_3d(", "def graph_point(", "def secant_line(",
        "def tangent_line(", "def dim_except(", "def restore_emphasis(",
        "def emphasize(", "def wrap_text(", "def fit_width(",
        "def strike_through(", "def cancel_terms(",
        "def riemann_rectangles(", "def scaled_bar(", "T = _Theme()",
    ])
    def test_kit_exposes_helpers(self, helper):
        assert helper in kit_source("math")

    def test_wrap_text_fits_frame(self):
        # simulate the kit's wrap_text logic against its own estimator
        source = kit_source("math")
        namespace: dict = {}
        exec(compile(source, "kit", "exec"), namespace)
        wrap_text = namespace["wrap_text"]
        long = ("Explain why hydrogen bromide adds to propene under "
                "Markovnikov's rule, describing the secondary and primary "
                "carbocation intermediates, their relative stabilities, "
                "the energy profile of both pathways, and why the major "
                "product is two bromopropane rather than one bromopropane.")
        rows = wrap_text(long, font_size=26)
        assert len(rows) >= 2
        assert all(len(r) <= 115 for r in rows)
        assert " ".join(rows) == long
        char_w = 26 * 0.0042
        assert all(len(r) * char_w <= 12.5 + char_w for r in rows)

    def test_fit_width_shrinks(self):
        source = kit_source("math")
        namespace: dict = {}
        exec(compile(source, "kit", "exec"), namespace)
        fit_width = namespace["fit_width"]
        mobj = namespace["Line"](np.array([0.0, 0.0, 0.0]),
                                 np.array([20.0, 0.0, 0.0]))
        assert mobj.width > 12.8
        fit_width(mobj)
        assert mobj.width <= 12.8 + 1e-6

    def test_kit_colors_inline(self):
        source = kit_source("math")
        assert "ManimColor('#65A9FF')" in source
        paper = kit_source("paper")
        assert "ManimColor('#2463A6')" in paper
