from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService
import numpy as np

# ──────────────────────────────────────────
# Scene 1 (placeholder)
# ──────────────────────────────────────────
class Intro(VoiceoverScene):
    pass

# ──────────────────────────────────────────
# Scene 2 – Position vector, Δr and Δs
# ──────────────────────────────────────────
class Scene2(VoiceoverScene):
    def construct(self):
        self.set_speech_service(GTTSService())

        # ── Origin at bottom-left ─────────────────────────────
        O = np.array([-5.0, -3.2, 0])

        x_axis = DashedLine(O, O + RIGHT * 5.5,
                            dash_length=0.18, color=GREY_B)
        y_axis = DashedLine(O, O + UP * 6.8,
                            dash_length=0.18, color=GREY_B)
        origin_dot   = Dot(O, radius=0.055, color=WHITE)
        origin_label = MathTex("O", font_size=34).next_to(O, DL, buff=0.12)

        # ── Custom curve: upward-sweeping cubic (not sine) ────
        #    Resembles the image path going from lower-centre → upper-right
        def curve_pt(t):
            x = O[0] + 1.2 + 2.8 * t + 0.15 * t ** 2
            y = O[1] + 0.2 + 0.4 * t + 1.3 * t ** 2
            return np.array([x, y, 0])

        T_START, T_A, T_AP, T_END = 0.0, 1.3, 1.75, 2.2

        pos_A  = curve_pt(T_A)
        pos_Ap = curve_pt(T_AP)

        curve_mob    = ParametricFunction(curve_pt,
                                          t_range=[T_START, T_END],
                                          color=GOLD)
        curve_dashed = DashedVMobject(curve_mob,
                                      num_dashes=28,
                                      dashed_ratio=0.55)

        path_label = (Text("Path of\nparticle", font_size=22, color=GOLD_A)
                      .next_to(curve_pt(T_END), UR, buff=0.15))

        # ── Points A and A′ ───────────────────────────────────
        dot_A  = Dot(pos_A,  color=RED, radius=0.07)
        dot_Ap = Dot(pos_Ap, color=RED, radius=0.07)

        lbl_A  = MathTex("A",  font_size=30).next_to(pos_A,  DR, buff=0.10)
        lbl_Ap = MathTex("A'", font_size=30).next_to(pos_Ap, UR, buff=0.10)

        # ── Vectors ───────────────────────────────────────────
        kw = dict(buff=0, stroke_width=2.5,
                  max_tip_length_to_length_ratio=0.07)

        vec_r    = Arrow(O,      pos_A,  color=WHITE, **kw)
        vec_rdr  = Arrow(O,      pos_Ap, color=WHITE, **kw)
        vec_dr   = Arrow(pos_A,  pos_Ap, color=WHITE,
                         buff=0, stroke_width=2.5,
                         max_tip_length_to_length_ratio=0.14)

        # label positions match the image layout
        lbl_r   = (MathTex(r"\mathbf{r}", font_size=32)
                   .next_to(vec_r.point_from_proportion(0.45),
                            LEFT, buff=0.12))
        lbl_rdr = (MathTex(r"\mathbf{r} + \Delta\mathbf{r}", font_size=28)
                   .next_to(vec_rdr.point_from_proportion(0.50),
                            LEFT, buff=0.12))
        lbl_dr  = (MathTex(r"\Delta\mathbf{r}", font_size=28)
                   .next_to(vec_dr.get_center(), RIGHT, buff=0.10))

        # ── Δs arc label ──────────────────────────────────────
        mid_arc = curve_pt((T_A + T_AP) / 2)
        lbl_ds  = (MathTex(r"\Delta s", font_size=26)
                   .next_to(mid_arc + RIGHT * 0.35, RIGHT, buff=0.05))

        # ═══════════════════════════════════════════════════════
        # Animation sequence with voiceovers
        # ═══════════════════════════════════════════════════════

        with self.voiceover(
                text="Consider a rectangular coordinate system with origin O."):
            self.play(
                Create(x_axis), Create(y_axis),
                FadeIn(origin_dot), Write(origin_label),
                run_time=1.5
            )
            self.wait(0.5)

        with self.voiceover(
                text="A particle moves along this curved path."):
            self.play(Create(curve_dashed), Write(path_label), run_time=2)
            self.wait(0.5)

        with self.voiceover(
                text="At some instant, the particle is at position A, "
                     "described by the position vector r from origin O."):
            self.play(FadeIn(dot_A), Write(lbl_A))
            self.play(GrowArrow(vec_r), Write(lbl_r))
            self.wait(0.5)

        with self.voiceover(
                text="After a small time interval delta t, it reaches "
                     "position A prime, described by the vector r plus delta r."):
            self.play(FadeIn(dot_Ap), Write(lbl_Ap))
            self.play(GrowArrow(vec_rdr), Write(lbl_rdr))
            self.wait(0.5)

        with self.voiceover(
                text="The change in position, delta r, is the vector "
                     "drawn directly from A to A prime."):
            self.play(GrowArrow(vec_dr), Write(lbl_dr))
            self.wait(0.5)

        with self.voiceover(
                text="Delta s is the actual arc length traveled along "
                     "the curve between A and A prime."):
            self.play(Write(lbl_ds))
            self.wait(1.2)