## Guide

The project is divided into 2 parts, one is the top level APIs and the other is services.

Each service is created according to DDD rules and is independent of each other. Each of the services
represents a bounded context, where everything is contained inside and only referencial information is
shared.

There are 3 services in this project,
- Sales
- Inventory
- Catalog

### Sales
Contains information about the sales and how much the time was sold for, since this part of the
context according to the problem description, does not deals with the SKUs and etc. only just
pricing information and a referencial tag to the inventory log so there is only one model in this
service. i.e. Sale

### Inventory
Contains information about the inventory in the form of logs, I am using logs because I don't want
to manage a state or sort of an integer where I am keeping track of the inventory, instead I am
keeping each record of what happened to the inventory.

Later we can use that information to compute the total inventory that we have right now.

### Catalog
This is a very simple service, it just contains information about the SKUs. this is a description of
what we SELL


### Communication between the services
The communication between the services is done using the an anti corruption layer, which is a design
pattern that uses interfaces to abstract information source for a external bounded context.
This is basically DIP principle that helps in testing the code, without using any code from the
external context

### APIs
Since the time was short for me to complete this, and this was communicated by the email I sent
early given no response, I had to submit and incomplete project.


## Installation
### create a virtual environment using the following command

```bash
    python -m venv venv
```

### install the dependancies using the following command

```bash
    pip install -r requirements.txt
```

### Database
You also need a postgres database to run this project.
That has not been dockerized yet.
So you will need something like Postgres.app or Postgres installed on your machine.

After that run the tests


## Questions

### If there are libraries essential for the project configuration, list them and explain the reason.
Right now there is only one which is pg-migrator, which is a nodejs module that helps in running
migrations on the database



### If there are libraries that you think might be necessary for project configuration, list them and explain the reason.
I can't think of anything

### The timezone of the data and the user's timezone may be different from your located timezone. What should be considered when handling Datetime using Python and Database? (Explanation or code example)
Everything should be stored in datetime/Timestamp with time zone format, thus we are storing the
timezone along with the timestamp and thus remove and ambiguity for errors

I have made a utility function that I am making use of in the code, which is giving my the now() time
in UTC timezone, which is the standard for all the timezones. now() is the most used function in the
datetime library and it is best to make a wrapper function that ensures timezone will always be utc

```python
def now_in_utc() -> datetime:
    """Current time in UTC time zone"""

    return datetime.now(timezone.utc)
```
