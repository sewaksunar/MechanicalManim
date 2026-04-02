## **Animation Methods in Manim**

There are several ways to create animations in Manim. Let me explain the main approaches:

---

## **1. Direct .animate Method** (Most Common)

```python
# Simple animation
self.play(square.animate.scale(2), run_time=1)
self.play(circle.animate.move_to(RIGHT * 3), run_time=1)
self.play(text.animate.set_color(RED), run_time=2)
```

**How it works:**
- `.animate` creates an animation of the property change
- Runs during `self.play()`
- Automatically interpolates between start/end values

**Common properties:**
```python
.animate.scale(2)              # Size
.animate.move_to(pos)          # Position
.animate.set_color(RED)        # Color
.animate.rotate(PI)            # Rotation
.animate.shift(UP * 2)         # Relative movement
.animate.set_opacity(0.5)      # Transparency
```

---

## **2. Built-in Animation Classes**

Manim provides pre-made animation classes for common effects:

```python
from manim import *

class AnimationDemo(Scene):
    def construct(self):
        square = Square()
        
        # Drawing animations
        self.play(Create(square))           # Draw object
        self.play(Write(Text("Hello")))     # Write text
        self.play(DrawBorderThenFill(square))  # Draw border then fill
        
        # Movement animations
        self.play(Move(square, RIGHT * 2))  # Direct movement
        self.play(ApplyMatrix(np.array([[2, 0], [0, 1]]), square))  # Matrix transform
        
        # Change animations
        self.play(ApplyMethod(square.scale, 2))  # Apply method
        self.play(FadeIn(square))           # Fade in
        self.play(FadeOut(square))          # Fade out
        
        # Morphing
        circle = Circle()
        self.play(Transform(square, circle))  # Morph shape
        self.play(TransformFromCopy(square, circle))  # Copy and morph
        
        # Rotation
        self.play(Rotating(square, angle=PI, axis=OUT))  # Rotate in 3D
        
        # Special effects
        self.play(Indicate(square, color=YELLOW))  # Highlight
        self.play(Flash(square))            # Flash effect
        self.play(Wiggle(square))           # Wobble
```

---

## **3. Using ValueTrackers + Updaters (Dynamic)**

```python
class ValueTrackerExample(Scene):
    def construct(self):
        value = ValueTracker(0)
        number = DecimalNumber(0)
        
        # Updater: function called every frame
        number.add_updater(
            lambda m: m.set_value(value.get_value())
        )
        
        self.add(number)
        self.play(value.animate.set_value(100), run_time=2)
        self.wait(1)
```

**How it works:**
- `ValueTracker` holds mutable value
- `add_updater()` runs function every frame
- When ValueTracker changes → updater function called
- Object updates in real-time

---

## **4. Using always_redraw()** (Your Pendulum Code)

```python
class AlwaysRedrawExample(Scene):
    def construct(self):
        angle = ValueTracker(0)
        
        # Rebuild circle position every frame
        circle = always_redraw(
            lambda: Circle(radius=0.5, color=BLUE)
                    .move_to(np.array([np.cos(angle.get_value()), 
                                      np.sin(angle.get_value()), 0]))
        )
        
        self.add(circle)
        self.play(angle.animate.set_value(2*PI), run_time=3)
```

**Difference from updater:**
- `always_redraw()`: **Recreates object completely** each frame
- `add_updater()`: **Modifies existing object** each frame
- `always_redraw()` = cleaner for complex geometry
- `add_updater()` = more efficient for simple changes

---

## **5. Custom Animation Class** (Like Your DampedPendulum)

```python
class CustomRotation(Animation):
    """Custom animation class for special effects."""
    
    def __init__(self, mobject, angle: float, **kwargs):
        super().__init__(mobject, **kwargs)
        self.angle = angle
        self.initial_angle = 0
    
    def interpolate_mobject(self, alpha: float) -> None:
        # alpha goes from 0 to 1
        current_angle = self.angle * alpha
        self.mobject.rotate(current_angle - self.initial_angle)
        self.initial_angle = current_angle


# Usage
class MyScene(Scene):
    def construct(self):
        square = Square()
        self.add(square)
        self.play(CustomRotation(square, angle=PI, run_time=2))
```

**When to use:**
- Complex physics (damping, forces)
- Non-standard interpolation
- Need frame-by-frame control

---

## **6. Add/Remove Methods**

```python
class AddRemoveExample(Scene):
    def construct(self):
        # Direct add (no animation)
        square = Square()
        self.add(square)
        
        # Visible (no animation)
        circle = Circle()
        circle.move_to(RIGHT * 2)
        self.add(circle)
        
        # Remove
        self.remove(square)  # Gone instantly
        
        # Multiple objects
        group = VGroup(Square(), Circle(), Triangle())
        self.add(group)
```

---

## **7. Chained Animations**

```python
class ChainedAnimations(Scene):
    def construct(self):
        square = Square()
        self.add(square)
        
        # Sequential
        self.play(square.animate.move_to(RIGHT), run_time=1)
        self.play(square.animate.scale(2), run_time=1)
        self.play(square.animate.rotate(PI), run_time=1)
        
        # Parallel (same self.play call)
        circle = Circle()
        self.add(circle)
        self.play(
            square.animate.move_to(UP),
            circle.animate.move_to(DOWN),
            run_time=1
        )
```

---

## **8. Rate Functions (Timing/Easing)**

```python
class RateFunctionExample(Scene):
    def construct(self):
        # Different easing curves
        square = Square()
        self.add(square)
        
        # Linear (constant speed)
        self.play(square.animate.move_to(RIGHT), rate_func=linear, run_time=1)
        
        # Smooth (ease in/out)
        self.play(square.animate.move_to(UP), rate_func=smooth, run_time=1)
        
        # Rush (slow start, fast end)
        self.play(square.animate.move_to(LEFT), rate_func=rush_in, run_time=1)
        
        # Slow (fast start, slow end)
        self.play(square.animate.move_to(DOWN), rate_func=rush_out, run_time=1)
        
        # Bounce
        self.play(square.animate.move_to(ORIGIN), rate_func=bounce, run_time=1)
```

---

## **9. Partial Animations (LagRatio)**

```python
class LagRatioExample(Scene):
    def construct(self):
        # Animate multiple objects with stagger
        circles = VGroup(*[Circle() for _ in range(5)])
        circles.arrange(RIGHT, buff=0.5)
        self.add(circles)
        
        # Each circle animates one after another
        self.play(
            circles.animate.scale(2),
            lag_ratio=0.2  # 20% delay between each
        )
```

---

## **10. Wait & Pause**

```python
class WaitExample(Scene):
    def construct(self):
        square = Square()
        self.add(square)
        
        # Wait (no animation)
        self.wait(1)        # Wait 1 second
        self.wait(0.5)      # Wait 0.5 second
```

---

## **Comparison Table**

| Method | When to Use | Performance | Complexity |
|--------|-------------|-------------|-----------|
| `.animate` | Simple property changes | Fast | Easy |
| Built-in classes | Standard effects (fade, rotate) | Fast | Easy |
| ValueTracker + updater | Dynamic values, counters | Medium | Medium |
| `always_redraw()` | Complex geometry, constraints | Slow | Hard |
| Custom Animation | Physics, special motion | Medium | Hard |
| Add/Remove | Static elements | Fast | Easy |

---

## **Your Pendulum Uses**

Your pendelum.py uses **Custom Animation Class**:
```python
class DampedPendulum(Animation):
    def interpolate_mobject(self, alpha: float) -> None:
        # Calculate physics each frame
        angle = damped_amplitude * sin(...)
        self.mobject.rotate(delta_angle)
```

**Why?** Because damped oscillation requires:
- Frame-by-frame control
- Physics calculation every frame
- Tracking previous state
- Custom interpolation

---

## **Best Practices**

```python
# ✅ Good: Simple and readable
self.play(square.animate.move_to(RIGHT * 2), run_time=1)

# ✅ Good: Multiple animations in parallel
self.play(
    square.animate.scale(2),
    circle.animate.move_to(UP),
    run_time=1
)

# ❌ Avoid: Too many sequential plays
self.play(...)
self.play(...)
self.play(...)
self.play(...)
# Instead, use lag_ratio

# ✅ Good: Use always_redraw only when needed
# (it's slower - rebuilds every frame)
```

Which animation method are you interested in exploring more?