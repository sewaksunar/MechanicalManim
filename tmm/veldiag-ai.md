## **Detailed Code Execution Flow**

I'll walk through exactly **what happens, when, and why** as the program runs.

---

## **INITIALIZATION PHASE** (Before Animation Starts)

### **1. Manim Loads the Scene**
```python
class SpaceDiag(Scene):
    def construct(self) -> None:
```
- Manim calls `SpaceDiag().construct()`
- Creates a blank 2D canvas

### **2. Create ValueTrackers** (Animation State)
```python
self.ang = ValueTracker(135 * DEGREES)  # crank angle = 2.356 radians
self.sft = ValueTracker(0.0)            # shift = 0 (no translation yet)
```
- These are **mutable state containers**
- Changed by `.animate` during animations
- Every other value derives FROM these

### **3. Create Getter Functions** (Compute Everything)
```python
self.get_o2 = lambda: interpolate(_ORIGIN_START, _ORIGIN_END, self.sft.get_value())
#              Returns: FROM origin_start TO origin_end, progress = sft value
```

| Getter | Returns |
|--------|---------|
| `get_o2()` | Fixed pivot O2 (slides from left to right as `sft` goes 0→1) |
| `get_o4()` | Fixed pivot O4 = O2 + (L1, 0) |
| `get_a()` | Crank endpoint = O2 + (L2·cos(ang), L2·sin(ang)) |
| `get_b()` | Coupler endpoint = circle_intersection(O2, L3, O4, L4) |

**Key**: These are **lambda functions** = when called, they read CURRENT tracker values.

### **4. Create Always_redraw Mechanism**
```python
mech = always_redraw(
    lambda: FourBarMechanism(self.get_o2(), self.ang.get_value())
)
self.add(mech)
```
- **`always_redraw(lambda: ...)`** wraps an object constructor
- **Every frame**, Manim:
  1. Calls the lambda
  2. Creates NEW FourBarMechanism from current tracker values
  3. Replaces old version on screen
- **Result**: Mechanism automatically moves/rotates with trackers

---

## **ANIMATION PHASES** (What Happens When)

### **PHASE 1: Crank Sweep Animation** (Time 0.0 → 4.0 seconds)

#### **Step A: Forward sweep (0→2s)**
```python
self.play(self.ang.animate.set_value(200 * DEGREES), rate_func=linear, run_time=2)
```

**Execution:**
- Timeline: 2000 milliseconds
- **Frame 0** (t=0):
  - `ang = 135°` (starting value)
  - `get_a()` returns crank at 135° angle
  - Mechanism redraws
  - Screen shows: mechanism at starting angle

- **Frame 1** (t=0.0333s):
  - `ang = 135° + (200-135)° × (0.0333/2) = 135° + 1.08° = 136.08°`
  - `get_a()` recomputes: now at 136.08°
  - `circle_intersections()` finds new B position
  - Mechanism redraws with new positions
  
- **Frame N** (middle, t=1.0s):
  - `ang = 135° + 65° × 0.5 = 167.5°` (halfway)
  - Everything updates
  
- **Frame FINAL** (t=2.0s):
  - `ang = 200°` (target reached)
  - Mechanism at final angle

#### **Step B: Reverse sweep (2s→4s)**
```python
self.play(self.ang.animate.set_value(135 * DEGREES), run_time=2)
```
- Animates back: 200° → 135°
- Same process in reverse
- **Total duration**: 4 seconds

---

### **PHASE 2: Translation to Right** (Time 4.0 → 5.5 seconds)

```python
self.play(self.sft.animate.set_value(1.0), run_time=1.5)
```

**Execution:**
- `sft` changes from 0.0 → 1.0 over 1.5 seconds
- `get_o2()` uses `interpolate(_ORIGIN_START, _ORIGIN_END, sft)`

```python
_ORIGIN_START = ORIGIN + DOWN * 2 + LEFT * 1   # (-1, -2)
_ORIGIN_END   = DOWN   * 2 + LEFT * 4          # (-4, -2)
```

- **t=0**: `sft=0` → `O2 = interpolate(..., 0) = (-1, -2)`
- **t=0.75**: `sft=0.5` → `O2 = (-2.5, -2)`
- **t=1.5**: `sft=1.0` → `O2 = (-4, -2)`

**What redraws:**
- `get_o2()` changes
- `get_o4()` = `get_o2() + (L1, 0)` changes
- `get_a()` = `get_o2() + (L2·cos, L2·sin)` changes
- `get_b()` = circle_intersection (new positions) changes
- **Whole mechanism slides right**

---

### **PHASE 3: Add Title** (Time 5.5 → 5.7 seconds)

```python
self.play(Write(Text("Crank-Rocker Mechanism", font_size=30).to_edge(UP)))
```
- Writes text at top (no moving objects affected)

---

### **PHASE 4: Build Velocity Polygon** (Time 5.7 → 8.0 seconds)

#### **Step 0: Highlight Joints (t=5.7s)**
```python
joints = always_redraw(lambda: VGroup(
    Dot(self.get_a(),  color=RED),
    Dot(self.get_b(),  color=RED),
    Dot(self.get_o2(), color=YELLOW),
    Dot(self.get_o4(), color=YELLOW),
))
self.play(Create(joints))
```

**Execution:**
1. Lambda captures getters
2. When called → computes current positions
3. `get_a()`, `get_b()`, `get_o2()`, `get_o4()` all return CURRENT values
4. 4 dots drawn at mechanism joints
5. `always_redraw` ensures they follow if mechanism moves

#### **Step 1: Draw v_A (t=5.9s)**
```python
va_poly = always_redraw(lambda: Arrow(
    pole,  # fixed point (3.5, 0.5)
    pole + perp_unit(self.get_a() - self.get_o2()) * _VEL_SCALE,
    # direction = perpendicular to (A - O2), length scaled
))
self.play(GrowArrow(va_poly), Write(va_poly_lbl))
```

**Execution:**
- Direction = perpendicular to crank
- **Why perpendicular?** In kinematics, velocity of a point on a rotating link is perpendicular to the link
- Drawn from `pole` (fixed reference point for velocity polygon)

#### **Step 2: Draw v_{B/O4} direction (t=6.1s)**
```python
vb_dir = always_redraw(lambda: DashedLine(
    pole,
    pole + perp_unit(self.get_b() - self.get_o4()) * _VEL_SCALE * 2.5,
    color=GREEN, dash_length=0.12,
))
```
- Direction = perpendicular to rocker link
- **Dashed** = magnitude unknown yet
- Extends long (2.5× scale) for visibility

#### **Step 3: Draw v_{B/A} direction (t=6.3s)**
```python
vba_dir = always_redraw(lambda: DashedLine(
    va_poly.get_end(),  # START from tip of v_A
    va_poly.get_end() + perp_unit(self.get_b() - self.get_a()) * _VEL_SCALE * 2.5,
    color=PURPLE,
))
```
- **Starts at tip of v_A**, not at pole
- This implements **vector addition**: v_B = v_A + v_{B/A}
- Direction = perpendicular to coupler

#### **Step 4: Find Intersection & Draw Solid Vectors (t=6.5s)**

```python
def get_b_poly() -> np.ndarray:
    d_vb  = perp_unit(self.get_b() - self.get_o4())
    d_vba = perp_unit(self.get_b() - self.get_a())
    va_tip = va_poly.get_end()
    pt = line_line_intersect(pole, d_vb, va_tip, d_vba)
    return pt
```

**Execution (when called each frame):**
1. Get current B position from mechanism: `self.get_b()`
2. Compute two direction vectors:
   - Green: perpendicular to (B - O4)
   - Purple: perpendicular to (B - A)
3. Find where two **infinite lines** intersect:
   - Line 1: from `pole` in green direction
   - Line 2: from `va_tip` in purple direction
4. **Return intersection point** = velocity polygon point B

**Why intersection?** 
- Constraint 1: B rotates around O4 → velocity is perpendicular to rocker
- Constraint 2: B moves relative to A → velocity is perpendicular to coupler
- Both constraints must be satisfied simultaneously → intersection

```python
vb_solid = always_redraw(lambda: Arrow(
    pole, get_b_poly(),  # from pole to intersection point
    buff=0, color=GREEN,
))
vba_solid = always_redraw(lambda: Arrow(
    va_poly.get_end(), get_b_poly(),  # from tip of v_A to intersection
    buff=0, color=PURPLE,
))
```
- Now solid arrows (magnitudes determined by geometry!)

---

### **PHASE 5: Animate Crank Again** (Time 8.0 → 14.0 seconds)

```python
self.play(
    self.ang.animate.set_value(175 * DEGREES),
    rate_func=smooth, run_time=3,
)
self.play(
    self.ang.animate.set_value(135 * DEGREES),
    rate_func=smooth, run_time=3,
)
```

**Execution (CRITICAL - shows power of always_redraw):**

- **Frame at t=8.0s** (`ang=135°`):
  - `get_b()` returns current B position
  - `get_b_poly()` computes velocity polygon point B
  - All arrows drawn correctly
  
- **Frame at t=9.0s** (`ang=154°`):
  - `self.ang.get_value()` returns 154°
  - `get_a()` recomputes: new crank tip position
  - `get_b()` recomputes: new coupler endpoint (circle-circle intersection changes)
  - `get_o4` stays same, but new B means new constraint
  - `get_b_poly()` recomputes intersection:
    - `d_vb` changes (B-O4 direction changed)
    - `d_vba` changes (B-A direction changed)
    - `line_line_intersect()` finds NEW intersection
  - All `always_redraw` lambdas re-execute:
    - Mechanism redraws at new angle
    - `va_poly` rotates (different A position)
    - `vb_dir` points new direction
    - `vba_dir` starts new point and points new direction
    - `b_dot` moves to new intersection
    - Solid arrows `vb_solid`, `vba_solid` resize/reorient
  
- **Result**: Entire animation synchronizes instantly! Everything moves together.

---

## **Execution Summary Timeline**

```
Time    Event                           Value Changes
────────────────────────────────────────────────────────
0.0s    Start animation                 ang=135°, sft=0.0
2.0s    Crank at 200°                   ang=200°, sft=0.0
4.0s    Crank back at 135°              ang=135°, sft=0.0
5.5s    Mechanism at right position     ang=135°, sft=1.0
5.7s    Show joint dots                 (no change)
5.9s    Draw v_A                        (no change)
6.1s    Draw v_B/O4 direction           (no change)
6.3s    Draw v_BA direction             (no change)
6.5s    Show intersection point B       (no change)
8.0s    Start crank animation again     ang→175° over 3s
11.0s   Back to starting angle          ang→135° over 3s
14.0s   End of animation                ang=135°, sft=1.0
```

---

## **Key Mechanism: always_redraw() Rebuild Cycle**

Each frame (60 times per second), Manim does:

```python
# Pseudocode for each always_redraw object
while animation_running:
    for mob in always_redraw_list:
        new_mob = mob.lambda_constructor()  # Call the lambda!
        replace_on_screen(old_mob, new_mob)
    render_frame()
    time += 1/60
```

---

## **Why This Design is Powerful**

| Problem | Solution | Benefit |
|---------|----------|---------|
| **Multiple moving parts** | `always_redraw` | Automatic sync |
| **Complex constraints** | Getters compute from trackers | Single source of truth |
| **Kinematic accuracy** | Math functions (circles, lines) | Physically correct |
| **Live updates** | Lambdas re-execute each frame | Smooth animation |

When you change **one** ValueTracker, **everything** updates automatically! 🎯