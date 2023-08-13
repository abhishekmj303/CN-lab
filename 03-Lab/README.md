---
title: "Lab 03: Single-Server Multi-Client Connection"
author: "Abhishek M J - CS21B2018"
from: markdown-implicit_figures
date: "09-08-2023"
geometry: left=1cm,right=1cm,top=1cm,bottom=1cm
wrap: preserve
---

# Problem Statement

Write a Server program with threads, where each thread can handle a single client.
- Ensure server get connected to multiple clients.
- All the client messages to be displayed in server.
- Provide a mechanism to disconnect the client.

# Implementation 1: Demonstrate with local loop IP

## `server.py`:

![server-1-1](img/server-1-1.png)
![server-1-2](img/server-1-2.png)


## `client.py`:

![client-1-1](img/client-1-1.png)

## Output:


![Output Implementation 1](img/term-1.png)

\break
\break

# Implementation 2: Connect with multiple client with different IPs

## `server.py` and `client.py`:

Same as above

## Output:

![Output Implementation 2](img/term-2-1.png)
![term-2-2](img/term-2-2.png)
![term-2-3](img/term-2-3.png)


# Implementation 3: Modify the program where server can send messages to specific client

## `server.py`:

![server-3-1](img/server-3-1.png)
![server-3-2](img/server-3-2.png)
![server-3-3](img/server-3-3.png)
![server-3-4](img/server-3-4.png)

## `client.py`:

![client-3-1](img/client-3-1.png)
![client-3-2](img/client-3-2.png)

## Output:

![Output Implementation 3](img/term-3.png)