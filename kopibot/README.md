# kopibot

A bot that parses Singaporean coffee/tea (kopi/teh) orders and publishes them to an MQTT broker locally.

## Dependencies

- [aiomqtt](https://github.com/sbtinstruments/aiomqtt) — async MQTT client
- [pydantic](https://docs.pydantic.dev/) — data validation and order modelling


## Usage
### Prerequisites
- Manage the local environment with [uv](https://github.com/astral-sh/uv)
- An MQTT broker running locally, for example [mosquitto](https://mosquitto.org/download/)

### Running the bot
Run the bot interactively:

```bash
uv run kopibot
```

Enter an order in plain text, e.g.:

```
kopi siew dai
teh o kosong ping
kopi c
```

The parsed order is published as JSON to the `kopitiam/orders` MQTT topic on `localhost`.

## Order Syntax

| Keyword     | Effect                        |
|-------------|-------------------------------|
| `kopi`      | Coffee base                   |
| `teh`       | Tea base                      |
| `kosong`    | No sugar                      |
| `siew dai`  | Less sugar (0.5)              |
| *(default)* | Full sugar (1.0)              |
| `o`         | No milk (black)               |
| `c`         | Evaporated milk               |
| *(default)* | Condensed milk                |
| `png`/`bing` | Iced                        |

## Development

Run tests:

```bash
uv run pytest
```
