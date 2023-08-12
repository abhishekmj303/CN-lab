---
title: "Tutorial 2: Network Devices"
author: "Abhishek M J - CS21B2018"
date: "09-08-2023"
geometry: "left=1cm,right=1cm,top=1cm,bottom=1cm"
# fontsize: 20pt
---

## Hub

A hub is a basic network device that connects multiple devices together in a single network segment. It operates at the physical layer of the OSI model and simply repeats any data it receives on one port to all other ports. This means that all devices connected to the hub will receive all traffic, regardless of whether it is intended for them or not. This can lead to congestion and performance problems on the network.

## Layer 2 Switch

A layer 2 switch is a more intelligent device than a hub. It operates at the data link layer of the OSI model and uses MAC addresses to forward traffic to the correct destination device. This prevents unnecessary traffic from being sent to other devices on the network, which can improve performance. Layer 2 switches also create separate collision domains for each port, which can help to reduce collisions and improve network performance.

## Layer 3 Switch

A layer 3 switch is a type of switch that can also operate at the network layer of the OSI model. This allows it to route traffic between different networks, which can be useful for connecting multiple subnets or VLANs together. Layer 3 switches are more expensive than layer 2 switches, but they can offer better performance and flexibility.

## Router

A router is a network device that connects two or more networks together. It operates at the network layer of the OSI model and uses IP addresses to route traffic between networks. Routers are essential for connecting different networks together and for providing internet access.

## Bridge

A bridge is a device that connects two or more networks together that use the same network protocol. It operates at the data link layer of the OSI model and uses MAC addresses to forward traffic between networks. Bridges are less intelligent than routers and cannot route traffic between different networks. However, they are less expensive and can be a good solution for connecting small networks together.

## Repeater

A repeater is a device that amplifies and regenerates a signal over a long distance. It operates at the physical layer of the OSI model and does not understand any network protocols. Repeaters are used to extend the range of a network cable.

## Differences

Device | Layer | Function | Pros | Cons
--- | --- | --- | --- | ---
Hub | Physical | Repeats all traffic | Simple, inexpensive | Slow, creates a single collision domain
Layer 2 Switch | Data Link | Forwards traffic based on MAC addresses | Faster than hub, creates separate collision domains | Cannot route traffic between networks
Layer 3 Switch | Network | Forwards traffic based on IP addresses | Can route traffic between networks | More expensive than layer 2 switch
Router | Network | Routes traffic between networks | Most versatile network device | Expensive
Bridge | Data Link | Forwards traffic based on MAC addresses | Similar to layer 2 switch, but cannot route traffic between networks | Less expensive than layer 2 switch
Repeater | Physical | Amplifies and regenerates a signal | Simple, inexpensive | Cannot understand network protocols