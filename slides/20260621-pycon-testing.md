---
title: Efficient Python Testing
sub_title: PyCon Singapore 2026
author: Yu Jia 
---

Introduction
---
<!-- column_layout: [1, 1] -->
<!-- column: 0 -->

# AI assisted development makes testing much simpler:
* Legacy migration: ensure behavioural stability
* Brownfield: increasing missing coverage
* Greenfield: good practices as the application grows
<!-- pause -->
<!-- column: 1 -->
# But it's not always the most efficient
* Dependent on prompts and context
* Generating tests based on code, or based on business logic?
* Tests generated might not be the easiest to read and debug

<!-- end_slide -->

Introduction
---
# Today's goals
<!-- column_layout: [1, 1] -->
<!-- column: 0 -->
* Learn what is available in Python for testing
* Start writing tests **without** AI
* Use AI to get the same (or better) results
<!-- column: 1 -->
# Types of tests
* Unit
* Integration
* End to End

Today we will focus on Unit Tests.

<!-- end_slide -->

Testing Principles
---
# Basic Principles:

```python
# Arrange: set up your environment, variables, data
x, y = 2, 5

# Act: execute the function, behaviour you are testing
z = add(x, y)

# Assert: check the outcomes of your action
assert z == 7
```

<!-- end_slide -->

Environment Setup
-------
<!-- column_layout: [1, 1] -->
<!-- column: 0 -->
Make sure you have `uv` installed locally.

Clone this repository:
# github.com/yujia21/pyconsg-2026-testing-workshop

Navigate into the `kopibot` sub-directory.

<!-- column: 1 -->
Initialize the environment:
```bash
uv sync
```

Try running the test:
```bash
uv run pytest
```

It should currently show as xpassed!


<!-- end_slide -->

Kopibot
---
<!-- column_layout: [1, 1] -->
<!-- column: 0 -->

Defines a pydantic class

```python
class Order(BaseModel):
    base: typing.Literal["teh", "kopi"]
    sugar: float
    condensed_milk: bool
    evaporated_milk: bool
    ice: bool
```
<!-- column: 1 -->
Parses an order into the class

```python
def parse_order(user_input: str) -> Order:
```

Sends the order via MQTT
```python
async def send_order(order: Order) -> None:
```

<!-- end_slide -->

Write your first unit test!
---

We'll use `pytest`. 
In a `src` layout, `pytest` will look for:
* all files in the folder `tests` with filenames starting with `test`
* all functions within these files with names starting in `test`.

# Project Layout
```
kopibot/
├── src/
│   └── kopibot/
│       └── main.py
├── tests/
│   ├── test_parse.py
```
<!-- end_slide -->

Write your first unit test!
---
Let's open `tests/test_parse.py`:
```python +exec:pytest
import pytest

@pytest.mark.xfail
def test_fail():
    pass
```

<!-- end_slide -->

Write your first unit test!
---
What should we test?

<!-- pause -->

# Parse Orders
<!-- pause -->
* Check each possible combination
* What happens if an order is not recognized?

<!-- pause -->
# Send Orders

<!-- pause -->
* What is the format of data sent?
* What happens if the server is not available?

<!-- end_slide -->

Write your first unit test!
---
Let's write a test to check the object parsed with the order "teh c png siew dai".
Remove the dummy test and replace it with `test_parse_order`. 

1. Arrange
2. Act
3. Assert

<!-- end_slide -->

Write your first unit test!
---

Run your test again with `uv run pytest`.

```python +exec:pytest
from kopibot.main import Order, parse_order

def test_parse_order():
    # arrange
    user_input = "teh c png siew dai"

    # act
    order = parse_order(user_input)

    # assert
    assert isinstance(order, Order)
    assert order.base == "teh"
    assert order.ice
```


<!-- end_slide -->

Write your first unit test!
---
What about a failure case? What if a user asks for "milo"?

```python +exec:pytest
import pytest

from kopibot.main import parse_order

def test_parse_bad_order():
    with pytest.raises(ValueError):
        parse_order("milo")
```

<!-- end_slide -->

Add some parametrization...
---

Now we want to test other drink orders... should we write one test per order type?

```python
def test_parse_order():
    # arrange
    user_input = "kopi o kosong"

    # act
    order = parse_order(user_input)

    # assert
    assert order == Order(
        base="kopi",
        ice=False,
        condensed_milk=False,
        evaporated_milk=False,
        sugar=0
    )
```

Imagine writing all possible variations... and then having to change them all!

This is too tedious!

<!-- end_slide -->

Add some parametrization...
---
Enter parametrization:
```python +exec:pytest
from datetime import datetime, timedelta

import pytest

@pytest.mark.parametrize(
    "end,start,expected",
    [
        (datetime(2001, 12, 12), datetime(2001, 12, 11), timedelta(1)),
        (datetime(2001, 12, 11), datetime(2001, 12, 12), timedelta(-1)),
    ]
)
def test_time_difference(end, start, expected):
    diff = end - start
    assert diff == expected
```
<!-- end_slide -->

Add some parametrization...
---
How would we do this here?

Let's try it for the following drinks:
* teh
* kopi png
* kopi o kosong
* teh c png siew dai

<!-- end_slide -->

Add some parametrization...
---
```python +exec:pytest
import pytest

from kopibot.main import Order, parse_order

@pytest.mark.parametrize(
    "user_input,expected",
    [
        ("teh", Order(base="teh", ice=False, condensed_milk=True, evaporated_milk=False, sugar=1)),
        ("kopi png", Order(base="kopi", ice=True, condensed_milk=True, evaporated_milk=False, sugar=1)),
        ("kopi o kosong", Order(base="kopi", ice=False, condensed_milk=False, evaporated_milk=False, sugar=0)),
        ("teh c png siew dai", Order(base="teh", ice=True, condensed_milk=False, evaporated_milk=True, sugar=0.5)),
    ]

)
def test_parse_order(user_input, expected):
    assert parse_order(user_input) == expected

```

<!-- end_slide -->

Fixtures
---

What if we need to re-use an object for other tests?

```python +exec:pytest
import pytest

from kopibot.main import Order, parse_order

def has_sugar(order: Order):
    return order.sugar

@pytest.fixture
def teh():
    return Order(base="teh", ice=False, condensed_milk=True, evaporated_milk=False, sugar=1)

def test_parse_order(teh):
    assert parse_order("teh") == teh

def test_has_sugar(teh):
    assert has_sugar(teh)
```

You can put all your fixtures in `tests/conftest.py` to share fixtures across files.

<!-- end_slide -->

Marks
---
Now how can we test the asynchronous function?

Make a new file: `test_send.py`.

```python +exec:pytest
import pytest

from kopibot.main import Order, send_order

@pytest.fixture
def teh():
    return Order(base="teh", ice=False, condensed_milk=True, evaporated_milk=False, sugar=1)

async def test_send_order(teh):
    await send_order(teh)

```
This does not work out of the box!

<!-- end_slide -->

Marks
---
Do:
```bash +exec
uv add --group dev pytest-asyncio
```

Then, mark tests with
```python
@pytest.mark.asyncio
async def test_send_order(teh):
    await send_order(teh)
```

and run your test again.

<!-- end_slide -->

Marks
---
We can mark any test with marks: `@pytest.mark.xxx`.

You've already seen some examples:
* parametrize: do multiple calls with different data
* xfail: expect it to fail

See all available marks with `pytest --markers`.

```bash +exec
pytest --markers
```
<!-- end_slide -->

Marks
---
Some libraries provide their own marks, for example, `pytest-asyncio`.

You can also customise marks:
```toml
[tool.pytest.ini_options]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
]
```

To run all tests that are not slow:
```bash
pytest -m "not slow"
```

Instead of adding a mark for pytest asyncio on every test, you can also configure it to be automatic in `pyproject.toml`:
```
[tool.pytest.ini_options]
asyncio_mode = "auto"
```
<!-- end_slide -->

Monkeypatch and mocks
---

# How should we test the MQTT integration?
```python
async with aiomqtt.Client(hostname="localhost", port=1883) as client:
    await client.publish("kopitiam/orders", payload.encode("utf-8"))
```

* We want to be able to run the tests in all environments: locally, in the CI, ... without requiring a connection to the broker
* We don't need to check that aiomqtt is actually publishing when we call publish
* We just need to check that we are connecting to the right broker, publishing to the right topic, with the right payload

## Monkeypatch
* Substitute libraries, environments, with what you want

## Mocks
* Helper objects provided by unittest to make testing simpler!

<!-- end_slide -->


Monkeypatch and mocks
---
```python +exec:pytest
import aiomqtt
import pytest

from unittest.mock import AsyncMock, Mock, MagicMock
from kopibot.main import Order, send_order

@pytest.fixture
def teh():
    return Order(base="teh", ice=False, condensed_milk=True, evaporated_milk=False, sugar=1)

@pytest.mark.asyncio
async def test_send_order(teh, monkeypatch):
    mock_client = AsyncMock()
    mock_context_manager = MagicMock()
    mock_context_manager.return_value.__aenter__.return_value = mock_client
    mock_context_manager.return_value.__aexit__.return_value = False
    monkeypatch.setattr(aiomqtt, "Client", mock_context_manager)

    mock_client.publish.assert_not_awaited()

    await send_order(teh)
    mock_client.publish.assert_awaited_once()

    # Add a breakpoint() here and see what other information you can get from mock_client.publish!
```


<!-- end_slide -->


Coverage
---
Install the coverage tool:
```bash
uv add --group dev coverage
```

Run your tests and collect coverage:
```bash
uv run coverage run -m pytest
```

Then view a report in the terminal:
```bash
uv run coverage report
```

Or generate an HTML report to explore in your browser:
```bash
uv run coverage html
```

<!-- end_slide -->


Now, let's use AI...
---
> "Generate unit tests for this library"

# Using Claude with no add ons:
* Basic use cases are covered: model class, parsing, sending
* Mocks out MQTT client
* No parametrisation or fixtures used

## Not an issue for a small library, but may lack consistency in complex libraries
<!-- end_slide -->

Now, let's use AI...
---
# Issues encountered with other tools:
* Prefer class based tests
* Not using `uv` by default

## Specify in your own skills or project's AGENTS.md
* Use parametrisation and fixtures where possible
* Prefer function based tests with pytest
* Prefer using uv for environment management

<!-- end_slide -->

Now, let's use AI...
---
# What are we validating?
* Important behaviour to your use case might not be validated based on inference from the code
* In this example, maybe we were supposed to handle orders with "milo" base properly as well
* Purely looking at the code, AI would have thought it was not needed

## Prompt and context matters:
* Does the AI tool know the requested feature and expected behaviour? (docs, conversation context...)
* Happy path bias: are there edge cases that are particular to your use case that are important to validate?


Iterate and iterate, and always review and understand AI-generated tests!

<!-- end_slide -->


Conclusion
---

# Generating unit tests with AI tools is easy nowadays, but requires validation!
## Knowing the available tools for readable and efficient tests helps you prompt better, and write better skills.

<!-- end_slide -->

Thank you!
---

<!-- column_layout: [1, 1] -->
<!-- column: 0 -->

# https://yujia21.github.io/
![LinkedIn](./linkedin.jpg)

<!-- column: 1 -->

# https://zenika.com
![Zenika](./zenika.png)
<!-- end_slide -->
