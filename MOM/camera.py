# https://discord.com/channels/581738731934056449/1124411812209774613/1124454208037462117

from manim import *

class axesIn3D(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes(
            x_range=[-5,5,1],
            y_range=[-5,5,1],
            z_range=[-5,5,1],
            x_length=7,
            y_length=7,
            z_length=7,
        )
        lbls = axes.get_axis_labels() 
        self.add(axes, lbls) 
        self.move_camera(phi=45 * DEGREES, theta=45 * DEGREES, run_time=4)
        self.wait()
        
        radius = 4*7/10

        phis = VGroup()   
        for phi in range(15,180,15):
            phis += Circle(radius=radius*np.sin(phi*DEGREES)).shift(radius*np.cos(phi*DEGREES)*OUT)
            phis += MathTex(r"\varphi={:.0f}^o".format(phi),color=RED).scale(0.5).rotate(angle=90*DEGREES, axis=RIGHT).shift([0,-radius*np.sin(phi*DEGREES),0.2+radius*np.cos(phi*DEGREES)]).rotate(135*DEGREES, axis=OUT, about_point=ORIGIN)

        thetas = VGroup()
        for theta in range(0,360,30):
            thetas += Arc(radius=radius, start_angle=10*DEGREES, angle=160*DEGREES, color=TEAL).rotate(90*DEGREES, axis=RIGHT, about_point=ORIGIN).rotate(90*DEGREES, axis=UP, about_point=ORIGIN).rotate(theta*DEGREES, axis=OUT, about_point=ORIGIN)
            thetas += MathTex(r"\theta={:.0f}^o".format(theta), color=TEAL).scale(0.5)
            thetas[-1].shift((1.1*radius-thetas[-1].get_left()[0])*RIGHT).rotate(theta*DEGREES, axis=OUT, about_point=ORIGIN)
        self.play(Create(phis))
        self.play(Create(thetas))


        self.move_camera(phi=45 * DEGREES, theta=45 * DEGREES, run_time=4)
        self.wait()
        self.move_camera(phi=45 * DEGREES, theta=(360+45) * DEGREES, rate_func=rate_functions.linear, run_time=6)
        self.wait()
        self.move_camera(phi=0 * DEGREES, theta=(360+45) * DEGREES, rate_func=rate_functions.linear, run_time=3)
        self.wait()
        self.move_camera(phi=180 * DEGREES, theta=(360+45) * DEGREES, rate_func=rate_functions.linear, run_time=6)
        self.wait()