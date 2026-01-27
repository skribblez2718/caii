# Test Patterns by Language

## Python (pytest)

### Basic Test Structure

```python
def test_function_name_scenario_expected():
    # Arrange
    input_data = create_test_data()

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected_value
```

### Test Class

```python
@pytest.mark.unit
class TestClassName:
    """Tests for ClassName."""

    def test_method_returns_expected_value(self):
        obj = ClassName()
        result = obj.method()
        assert result == expected
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double_returns_twice_input(input, expected):
    assert double(input) == expected
```

### Fixtures

```python
@pytest.fixture
def sample_data():
    return {"key": "value"}

def test_uses_fixture(sample_data):
    assert sample_data["key"] == "value"
```

### Factory Fixtures

```python
@pytest.fixture
def create_user():
    def _create(name="Test", email="test@example.com"):
        return User(name=name, email=email)
    return _create

def test_user_creation(create_user):
    user = create_user(name="Custom")
    assert user.name == "Custom"
```

### Mocking

```python
from unittest.mock import patch, MagicMock

def test_external_call(mocker):
    mocker.patch("module.external_function", return_value="mocked")
    result = function_that_calls_external()
    assert result == "mocked"
```

### Exception Testing

```python
def test_raises_value_error():
    with pytest.raises(ValueError) as exc_info:
        function_that_raises()
    assert "expected message" in str(exc_info.value)
```

---

## Test Naming Conventions

### Pattern

```
test_<what>_<scenario>_<expected_outcome>
```

### Examples

| Name | Tests |
|------|-------|
| `test_add_positive_numbers_returns_sum` | Basic addition |
| `test_divide_by_zero_raises_error` | Error case |
| `test_empty_list_returns_none` | Edge case |
| `test_user_without_email_uses_default` | Default behavior |

---

## Test Categories

### Unit Tests

- Test single function/method
- No external dependencies
- Fast execution (< 10ms)

### Integration Tests

- Test component interactions
- May use database, file system
- Moderate speed (< 100ms)

### End-to-End Tests

- Test full workflows
- Use real dependencies
- Slower execution

---

## Markers

```python
@pytest.mark.unit
@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.fsm
@pytest.mark.critical
```

Run specific markers:

```bash
pytest -m unit
pytest -m "integration and not slow"
```
