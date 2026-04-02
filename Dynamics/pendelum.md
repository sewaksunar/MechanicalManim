## Syntax & OOP Explanation

### **Classes & Inheritance**

```python
class DampedPendulum(Animation):
```
- `class` - Creates a new class (a blueprint)
- `DampedPendulum` - Class name (custom animation)
- `(Animation)` - **Inheritance**: Inherits from Manim's `Animation` class
  - Gains all methods/properties from `Animation`
  - Can override methods (customize behavior)

---

### **Methods**

#### **1. `__init__` (Constructor)**
```python
def __init__(self, pendulum, amplitude: float, damping: float = 0.1, **kwargs):
```
- Called when creating a new instance: `DampedPendulum(pendulum, ...)`
- **`self`** - Reference to the current object (required first parameter)
- **Parameters with types** (`amplitude: float`) - Type hints (documentation)
- **Default values** (`damping: float = 0.1`) - Optional, uses default if not provided
- **`**kwargs`** - "Keyword arguments" - captures extra parameters and passes to parent

```python
super().__init__(pendulum, **kwargs)
```
- `super()` - Calls parent class (`Animation`) method
- Initializes the parent class properly

#### **2. `interpolate_mobject` (Override Method)**
```python
def interpolate_mobject(self, alpha: float) -> None:
```
- Overrides parent class method
- Called repeatedly during animation (0 to 1 progress)
- **`alpha`** - Animation progress (0.0 = start, 1.0 = end)
- **`-> None`** - Returns nothing

#### **3. `construct` (Manim Scene Method)**
```python
def construct(self):
```
- Scene's main method where animation is defined
- Manim automatically calls this

---

### **Instance Variables (Attributes)**

```python
self.amplitude = amplitude
self.damping = damping
self.previous_angle = 0
```
- **`self.`** - Belongs to the object (instance variable)
- Each object has its own copy
- Accessible throughout the class

---

### **OOP Concepts in Your Code:**

#### **1. Encapsulation**
```python
class DampedPendulum:
    # Variables grouped together
    self.amplitude
    self.damping
    self.previous_angle
```
- Groups related data & methods in one class
- Hides complexity

#### **2. Inheritance**
```python
class DampedPendulum(Animation):  # Inherits from Animation
    super().__init__()             # Call parent's __init__
```
- Reuses code from parent class (`Animation`)
- Inherits: `.play()`, rotation logic, timing

#### **3. Polymorphism (Method Overriding)**
```python
def interpolate_mobject(self, alpha):  # Override parent method
```
- Parent `Animation` has this method
- We override it with custom logic
- Parent class expects it—automatically called

#### **4. Abstraction**
```python
# Complex physics hidden in one method
def interpolate_mobject(self, alpha):
    damped_amplitude = self.amplitude * np.exp(-self.damping * alpha)
    angle = damped_amplitude * np.sin(2 * np.pi * self.frequency * alpha)
```
- User just calls `DampedPendulum(...)` without understanding the math
- Complex behavior simplified to one line

---

### **Python Syntax Specifics:**

| Syntax | Meaning |
|--------|---------|
| `class ClassName:` | Define a class |
| `def method(self, param):` | Define a method |
| `self` | Reference current object |
| `**kwargs` | Accept any keyword arguments |
| `->` Type | Return type hint |
| `: type` | Parameter type hint |
| `= default` | Optional parameter value |
| `super()` | Call parent class method |
| `@` | Decorator (modifies function) |
| `self.var` | Instance variable |

---

### **Flow of Execution:**

```
1. DampedPendulum(pendulum, ...) created
   ↓
2. __init__ called (setup: amplitude, damping, frequency)
   ↓
3. self.play() called (starts animation)
   ↓
4. interpolate_mobject() called 60+ times (each frame)
   ↓
5. Rotates pendulum with decaying amplitude
```

Does this clarify the OOP structure? Ask if you want deeper explanation on any part!