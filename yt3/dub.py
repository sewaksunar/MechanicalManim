from manim import *
from reactive_manim import * # for math labels that update with moving points
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
        axes_ptn = Axes(
            x_range=[0, 3, 1],
            y_range=[0, 3, 1],
            x_length=3,
            y_length=3,
            axis_config={"color": GREY_B, 
                        "stroke_width": 2.5, 
                        "include_tip": True, 
                        "tip_length": 0.15, 
                        },
        )
        axes_ptn.move_to(ORIGIN)
        self.play(Create(axes_ptn), run_time=2)

        # curve path of particle
        def curve_pt(t):
            start_point = np.array([1.5, 1.8, 0])
            control_point_1 = np.array([1.8, 1.1, 0])
            control_point_2 = np.array([3.5, 1.5, 0])
            end_point = np.array([4, 4, 0])
            return (
                (1 - t) ** 3 * start_point
                + 3 * (1 - t) ** 2 * t * control_point_1
                + 3 * (1 - t) * t**2 * control_point_2
                + t**3 * end_point
            )
        curve_mob = axes_ptn.plot_parametric_curve(curve_pt, t_range=[0, 1], color=GOLD)
        self.play(Create(curve_mob), run_time=3)

        path_label = Text("path of motion",
                        font_size=22, 
                        color=GOLD_A).next_to(curve_pt(1), 
                                            LEFT+DOWN*4,
                                            buff=0.15)
        self.play(Write(path_label), run_time=1)
        self.wait(0.5)
        self.remove(path_label)

        def get_pt(t):
            return axes_ptn.c2p(*curve_pt(t)[:2])
        
        # point P moving along the curve
        t_tracker = ValueTracker(0)
        dot_P = always_redraw(
            lambda: Dot(get_pt(t_tracker.get_value()), 
                        color=RED, 
                        radius=0.07
                        )
        )

        self.play(Create(dot_P), run_time=1)
        self.wait(0.5)
        self.play(t_tracker.animate.set_value(1), 
                  run_time=2, 
                  rate_func=linear)
        self.wait(0.5)
        self.remove(dot_P)




        # point A and A'
        pt_P = get_pt(0.1)
        pt_Pp = get_pt(0.4)
        dot_P = Dot(pt_P, color=RED, radius=0.07)
        lbl_P = MathTex("P", font_size=30).next_to(pt_P, UR, buff=0.1)

        dot_Pp = Dot(pt_Pp, color=RED, radius=0.07)
        lbl_Pp = MathTex("P'", font_size=30).next_to(pt_Pp, UP, buff=0.1)

        ## dot P and P' moving along the curve
        tracker_P = ValueTracker(0.1)
        self.add(dot_P, lbl_P)
        dot_P = always_redraw(
            lambda: Dot(get_pt(tracker_P.get_value()), 
                        color=RED, 
                        radius=0.07
                        )
        )
        self.play(Create(dot_P), run_time=1)
        self.play(tracker_P.animate.set_value(0.4), 
                  run_time=2)
        self.wait(0.5)
        self.add(dot_Pp, lbl_Pp)
        self.play(Create(dot_Pp), run_time=1)
        self.wait(0.5)

        # in time interval Δt
        lbl_dt = MathTex(r"\Delta t", font_size=28).next_to(pt_Pp, DL*2, buff=0.1)
        self.play(Write(lbl_dt), run_time=1)
        self.play(lbl_dt.animate.shift(DOWN*0.3), run_time=0.5)
        self.wait(0.5)

        # hilgiht paht from P to P'
        pathPPp = axes_ptn.plot_parametric_curve(curve_pt, t_range=[0.1, 0.4], color=BLUE, stroke_width=6)
        
        # path delta s label 
        path_lbl = MathTex(r"\Delta s", font_size=24, color=BLUE).next_to(pt_Pp, DL*2, buff=0.1)
        
        self.play(Create(pathPPp), Write(path_lbl), run_time=1)

        del_s_t = VGroup(lbl_dt, path_lbl)

        # ------------------
        # average speed : scalar quantity defined as Δs/Δt
        #-------------------
        lbl_avg_speed = MathTex(r"\frac{\Delta s}{\Delta t}", font_size=24).next_to(pt_Pp, DL*2, buff=0.1)
        self.play(Transform(del_s_t, lbl_avg_speed), run_time=1)
        self.wait(0.5)

        comp_lbl_avg_spped = MathTex(r"v_{\text{avg}} = \frac{\Delta s}{\Delta t}", font_size=24).next_to(pt_Pp, DL*2, buff=0.1)
        self.play(Transform(lbl_avg_speed, comp_lbl_avg_spped), run_time=1)
        self.remove(del_s_t)
        self.play(FadeOut(lbl_avg_speed), run_time=0.5)
        self.wait(0.5)
        self.remove(pathPPp)

        #-------------------
        # average velocity : vector quantity defined as Δr/Δt
        #-------------------

        # position vector r from origin O to point P
        O = axes_ptn.c2p(0, 0)
        vec_r = Arrow(O, pt_P, 
                      color=RED, 
                      buff=0, 
                      stroke_width=2.5, 
                      max_tip_length_to_length_ratio=0.07)
        lbl_r = MathTex(r"\mathbf{r}", font_size=32, color=RED).next_to(vec_r.point_from_proportion(0.6), LEFT, buff=0.12)
        or_lbl_r = MathTex(r"\vec{r}", font_size=32, color=RED).next_to(vec_r.point_from_proportion(0.6), LEFT, buff=0.12)
        self.play(Create(vec_r), run_time=1)
        # the the potion vector r label with bold letter r for simplitcity or with an arrow on top
        self.play(Transform(lbl_r, or_lbl_r), run_time=1)

        # position vector r + Δr from origin O to point P'
        vec_rdr = Arrow(O, pt_Pp, 
                        color=BLUE,
                        buff=0,
                        stroke_width=2.5,
                        max_tip_length_to_length_ratio=0.07)
        lbl_rdr = MathTex(r"\vec{r}", r"+", r"\Delta\vec{r}", font_size=28).next_to(vec_rdr.point_from_proportion(0.6), DR, buff=0.012)
        lbl_rdr[0].set_color(RED)
        lbl_rdr[2].set_color(GREEN)

        self.play(Create(vec_rdr), run_time=1)
        self.play(Create(lbl_rdr), run_time=1)

        # vector Δr from point P to P'
        vec_dr = Arrow(pt_P, pt_Pp, 
                        color=GREEN,
                        buff=0,
                        stroke_width=2.5,
                        max_tip_length_to_length_ratio=0.14)
        lbl_dr = MathTex(r"\Delta\vec{r}", font_size=28, color=GREEN).next_to(vec_dr.get_end() + RIGHT , LEFT, buff=0.1)
        self.play(Create(vec_dr), run_time=1)
        self.play(Write(lbl_dr), run_time=1)

        # del t label next to point P'
        lbl_dt = MathTex(r"\Delta t", font_size=28).next_to(lbl_dr, DOWN, buff=0.1)
        self.play(Write(lbl_dt), run_time=1)
        
        # del r by del t label for average velocity
        lbl_avg_vel = MathTex(r"\frac{\Delta\vec{r}}{\Delta t} = \text{average velocity}", font_size=28).next_to(lbl_dr, DR, buff=0.1)
        lbl_avg_vel[0][0:2].set_color(GREEN)
        lbl_avg_vel[0][3:5].set_color(WHITE)
        self.remove(lbl_dr)
        self.play(Transform(lbl_dt, lbl_avg_vel), run_time=1)

        # instantaneous velocity reduction form average velocity
        lbl_inst_vel = MathTex(r"\lim_{\Delta t \to 0} \frac{\Delta\vec{r}}{\Delta t} = \text{instantaneous velocity}", font_size=28).next_to(lbl_dr, DR, buff=0.1)
        lbl_inst_vel[0][0:2].set_color(GREEN) 
        lbl_inst_vel[0][3:5].set_color(WHITE)
        self.play(Transform(lbl_dt, lbl_inst_vel), run_time=5)
        
        lbl_ds_dt = MathTex(r"\frac{d \vec{r}}{dt} = \text{instantaneous velocity}", font_size=28).next_to(lbl_dr, DR, buff=0.1)
        self.play(Transform(lbl_dt, lbl_ds_dt), run_time=1)


