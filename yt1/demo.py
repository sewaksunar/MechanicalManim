from manim import *

class Step3(Scene):

    def construct(self):

        t1=MathTex(r"\lim_{n \to \infty}\sum^n_{i=1}",r"\left(\left(",r"3i",r"\cdot\frac{10}{n}-1\right)\cdot\frac{10}{n}\right)")

        t2=MathTex(r"\lim_{n \to \infty}\sum^n_{i=1}",r"\left(",r"3i",r"\cdot\frac{100}{n^2}-\frac{10}{n}\right)")

        t2n=MathTex(r"\lim_{n \to \infty}",r"\sum^n_{i=1}",r"\left(3i\cdot\frac{100}{n^2}",r"-",r"\frac{10}{n}",r"\right)")

        t3=MathTex (r"\lim_{n \to \infty}",r"\left(\sum^n_{i=1}",r"\left(3i\cdot\frac{100}{n^2}",r"\right)-\sum^n_{i=1}",r"\frac{10}{n}",r"\right)")

        t3n=MathTex(r"\lim_{n \to \infty}\left(\sum^n_{i=1}",r"",r"\left(",r"3i",r"\cdot\frac{100}{n^2}",r"\right)-",r"\sum^n_{i=1}",r"\frac{10}{n}\right)")

        t4=MathTex (r"\lim_{n \to \infty}\left(\sum^n_{i=1}",r"3i",r"",r"\cdot\frac{100}{n^2}",r"-",r"n\cdot",r"\frac{10}{n}\right)")

        t4n=MathTex(r"\lim_{n \to \infty}\left(",r"\sum^n_{i=1}",r"3",r"i\cdot\frac{100}{n^2}-",r"n\cdot\frac{10}{n}",r"\right)")

        t5=MathTex (r"\lim_{n \to \infty}\left(",r"3",r"\sum^n_{i=1}",r"i\cdot\frac{100}{n^2}-",r"10",r"\right)")

        t5n=MathTex(r"\lim_{n \to \infty}\left(3",r"\sum^n_{i=1}i",r"\cdot\frac{100}{n^2}-10\right)")

        t6=MathTex (r"\lim_{n \to \infty}\left(3",r"\cdot\frac{(1+n)(n)}{2}",r"\cdot\frac{100}{n^2}-10\right)")

        t6n=MathTex(r"\lim_{n \to \infty}\left(",r"3\cdot\frac{(1+n)(n)}{2}\cdot\frac{100}{n^2}",r"-10\right)")

        t7=MathTex (r"\lim_{n \to \infty}\left(",r"\frac{3\cdot(1+n)(n)\cdot 100}{2n^2}",r"-10\right)")

        t7n=MathTex(r"\lim_{n \to \infty}\left(",r"\frac{3\cdot(1+n)(n)\cdot 100}{2n^2}",r"-10\right)")

        t8=MathTex (r"\lim_{n \to \infty}\left(",r"\frac{300\cdot(1+n)}{2n}",r"-10\right)")

        t8n=MathTex(r"\lim_{n \to \infty}",r"\left(",r"\frac{300\cdot(1+n)}{2n}-10",r"\right)")

        t9=MathTex (r"\lim_{n \to \infty}",r" ",r"\frac{300\cdot(1+n)}{2n}-10",r" ")

        t9n=MathTex(r" ",r"\lim_{n \to \infty}",r"\frac{300\cdot(1+n)}{2n}",r"-10")

        t10=MathTex (r"150",r"\lim_{n \to \infty}",r"\frac{(1+n)}{n}",r"-10")

        t10n=MathTex(r"150\lim_{n \to \infty}",r"\frac{(1+n)}{n}",r"-10")

        t11=MathTex (r"150\lim_{n \to \infty}",r"\frac{\frac{1}{n}+\frac{n}{n}}{\frac{n}{n}}",r"-10")

        t12=MathTex (r"150\lim_{n \to \infty}",r"\frac{0+\frac{n}{n}}{\frac{n}{n}}",r"-10")

        t13=MathTex (r"150\lim_{n \to \infty}",r"\frac{\frac{n}{n}}{\frac{n}{n}}",r"-10")

        t13n=MathTex(r"150",r"\lim_{n \to \infty}\frac{\frac{n}{n}}{\frac{n}{n}}",r"-10")

        t14=MathTex (r"150",r"\cdot1",r"-10")

        t14n=MathTex(r"150\cdot1",r"-10")

        t15=MathTex (r"150",r"-10")

        t15n=MathTex(r"150-10")

        t16=MathTex (r"140")

        self.play(Write(t1))

        self.play(ReplacementTransform(t1,t2))

        self.replace(t2,t2n)

        self.play(ReplacementTransform(t2n,t3))

        self.replace(t3,t3n)

        self.play(ReplacementTransform(t3n,t4),FadeOut(t3n[1]))

        self.replace(t4,t4n)

        self.play(ReplacementTransform(t4n,t5))

        self.replace(t5,t5n)

        self.play(ReplacementTransform(t5n,t6))

        self.replace(t6,t6n)

        self.play(TransformMatchingShapes(t6n,t7))

        self.replace(t7,t7n)

        self.play(ReplacementTransform(t7n,t8))

        self.replace(t8,t8n)

        self.play(ReplacementTransform(t8n,t9),FadeOut(t8n[1]),FadeOut(t8n[3]))

        self.replace(t9,t9n)

        self.play(ReplacementTransform(t9n,t10))

        self.replace(t10,t10n)

        self.play(ReplacementTransform(t10n,t11))

        self.play(ReplacementTransform(t11,t12))

        self.play(TransformMatchingShapes(t12,t13))

        self.replace(t13,t13n)

        self.play(ReplacementTransform(t13n,t14))

        self.replace(t14,t14n)

        self.play(ReplacementTransform(t14n,t15))

        self.replace(t15,t15n)

        self.play(ReplacementTransform(t15n,t16))

        self.play(FadeOut(t16))

        self.wait()

        ans1=MathTex(r"f(x)=3x-1").shift(UP*1.5)

        ans2=MathTex(r"F(x)=\frac{3}{2}x^2-x").next_to(ans1,DOWN,buff=0.5)

        ans3=MathTex(r"\int_{0}^{10}(3x-1)\,dx=",r"F(10)-F(0)=\frac{3}{2}\cdot 100-10=150-10=",r"140").scale(0.8).next_to(ans2,DOWN,buff=0.5)

        ans4=MathTex(r"\int_{0}^{10}(3x-1)\,dx=",r" ",r"140")

        r=SurroundingRectangle(ans4[2])

        G=VGroup(ans1,ans2,ans3)

        self.play(Write(G))

        self.wait()

        self.play(FadeOut(ans1,ans2,ans3[1]),run_time=0.5)

        self.play(TransformMatchingShapes(ans3[0],ans4[0]),TransformMatchingShapes(ans3[2],ans4[2]))

        self.play(Write(r))

        self.play(FadeOut(r))