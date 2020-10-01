# CRH BotNet

A complete documentation can be found [here](https://docs.jerie.wang/crh-botnet/).

## Installation

Clone or download the repository, then

```bash
python3.7 setup.py install
```

You can also install from pip

```bash
python3.7 -m pip install crh-botnet
```

## Running The Server

You can run the development server by

```bash
python3.7 -m crh_botnet.server
```

You can also change the listening address and/or port

```bash
python3.7 -m crh_botnet.server -h 127.0.0.1 -p 8000
```

Defaults to `0.0.0.0:5003`
