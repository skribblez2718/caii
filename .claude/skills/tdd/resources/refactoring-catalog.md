# Refactoring Catalog

## Refactoring Safety Rules

1. **One change at a time** - Single atomic refactoring
2. **Test after each change** - Verify tests still pass
3. **Don't add features** - Behavior stays the same
4. **Commit incrementally** - Small, reversible changes

---

## Common Refactorings

### Extract Function

**Before:**
```python
def process_order(order):
    # Calculate total
    total = 0
    for item in order.items:
        total += item.price * item.quantity
    # Apply discount
    if order.customer.is_premium:
        total *= 0.9
    return total
```

**After:**
```python
def process_order(order):
    total = calculate_total(order.items)
    return apply_discount(total, order.customer)

def calculate_total(items):
    return sum(item.price * item.quantity for item in items)

def apply_discount(total, customer):
    return total * 0.9 if customer.is_premium else total
```

---

### Replace Magic Number with Constant

**Before:**
```python
def calculate_area(radius):
    return 3.14159 * radius * radius
```

**After:**
```python
PI = 3.14159

def calculate_area(radius):
    return PI * radius * radius
```

---

### Introduce Explaining Variable

**Before:**
```python
if user.age >= 18 and user.has_license and not user.is_banned:
    allow_access()
```

**After:**
```python
is_adult = user.age >= 18
is_eligible = user.has_license and not user.is_banned
can_access = is_adult and is_eligible

if can_access:
    allow_access()
```

---

### Replace Conditional with Early Return

**Before:**
```python
def get_payment_amount(order):
    if order.is_cancelled:
        return 0
    else:
        if order.is_shipped:
            return order.total
        else:
            return order.total * 0.9
```

**After:**
```python
def get_payment_amount(order):
    if order.is_cancelled:
        return 0
    if order.is_shipped:
        return order.total
    return order.total * 0.9
```

---

### Extract Class

**Before:**
```python
class Order:
    def __init__(self):
        self.customer_name = ""
        self.customer_email = ""
        self.customer_address = ""
        self.items = []
```

**After:**
```python
class Customer:
    def __init__(self, name, email, address):
        self.name = name
        self.email = email
        self.address = address

class Order:
    def __init__(self, customer):
        self.customer = customer
        self.items = []
```

---

### Rename for Clarity

**Before:**
```python
def calc(d, r):
    return d * r / 100
```

**After:**
```python
def calculate_discount(original_price, discount_percent):
    return original_price * discount_percent / 100
```

---

## Code Smells to Address

| Smell | Refactoring |
|-------|-------------|
| Duplicate code | Extract function |
| Long function | Extract function |
| Magic numbers | Extract constant |
| Complex conditional | Extract explaining variable |
| Deep nesting | Early returns |
| Poor naming | Rename |
| Large class | Extract class |
| Long parameter list | Introduce parameter object |

---

## Quality Metrics

| Metric | Target |
|--------|--------|
| `make lint` | 10/10 |
| `make format` | No changes |
| Function length | < 20 lines |
| Nesting depth | < 3 levels |
| Cyclomatic complexity | < 10 |
