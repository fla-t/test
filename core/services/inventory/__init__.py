"""
First before I even write a single line of code for the inventory service,
I need to model the domain that I'm going to be working with.

Since this is a test and I don't have a lot knowledge to begin with, I am just going to assume that
our business runs on the following processes

- Inventory is received
- Inventory is stored
- Inventory is stored

Let's say inventory is sent from the manufacturer or the distributor whatever is in this case,
and store it in some warehouse of ours (i am not going to model the warehouse, just for the sake of
simplicity)

Now, each inventory that we receive consists of some items or SKUs (formal term), and the have their
description, name and quantity

So, I am going to model the inventory as follows

Entities in our modeling are:
    - Inventory Log

"""
