MongoDB with FastAPI

Simplistic TODO API on top of MongoDB.

## Prerequisites
- Python +3.9.0
- MongoDB Database

## Environment Variables

### Windows
    $ set MONGODB_URL=<your url>

### Mac/Linux
    $ export MONGODB_URL=<your-url>


## Install and Start

    $ pip install -r requirements

    $ uvicorn app:app --reload