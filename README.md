# Capstone Project
## Contents

- [Introduction](#introduction)
- [Research](#research)
- [Requirements](#requirements)
- [Scope](#scope)
- [MVP](#mvp)
- [Application Architecture](#application-architecture)
- [Timeline](#timeline)
- [Resources](#resources)
- [How to use](#how-to-use)

## Introduction

The basic end goal of this project is to create a n-player game where human players conversate with m bots, where n is the number human players and m is the number of bots. 

## Research

### What is the turing test?

[The turing test](https://plato.stanford.edu/entries/turing-test/) is a test purposed by Allen Turing in 1949. It is a test of computers against the intellect of humans. It is performed with two humans, the *human* and the *interrogator*, and one computer whose goal is to impersonate a human. The interrogator will ask questions to the human and computer for 5 minutes. Turing thought that digital computers would, with enough computational power, be able to fool the interrogator 70% of the time. This happens to be a very difficult task something that LLM have only recently been able to accomplish well. 

In the context of this project we will wrestle with this test and I think if we succeed in making bots able to fool a human player into thinking they are a human we’ll be successful. In making the game bigger however and making the game more centered around questioning I think it may make it simpler for computers to imitate humans. Every person is both and interrogator and a player so it will be difficult for one to make obscure questioning line with out skepticism. I hypothesize this will make the corpus of language used inside of the game much smaller and therefore easier to duplicate. I think the most difficult thing to replicate is mistakes that human players will make. It will be interesting to see if we can successfully create a text corpus to duplicate mistakes well and be able to confuse a variety of people from different ages and backgrounds. Further research in its ability to play the game in other languages could also be interesting.

## Requirements

- Unit and Integration tests
- Web UI
- Support n users, where n > 1
- Support m AI models, where m >= 2
- AI models specifically trained inside of the game

## Scope

Ultimately the end product should be an engaging game that demonstrates the current state of the turing test with the aid of LLMs. The sign we have reached our goal is the capability of our model(s) to fool a human player into thinking the model is also human. Furthermore, if the bots themselves struggle to distinguish humans from the bots we have accomplished our goal.

## MVP 

With the AI model being the most unknown and potentially time consuming part of this project I think it is important we build out a low fidelity interface for the AI bots. The easier it is to interface the bots with the application the better and faster we can work to create the best bots. Also, the application should hopefully be designed with plenty of responsiveness with timing and latency being a factor in the game. I propose we design and build out a proper backend and web API. Then we can build out a front end to update a use r on the state of the game and use those same API calls to communicate with the bots what the state of the game is. For its current purposes the bots can respond the same way each time or answer basic questions based off pre generated lists.

- Backend that will serve the initial HTML/CSS/JS
- Web API that will update game state/data for the frontend with the JS
- Backend should manage connections either with session cookies

## Application Architecture

![Architecture](/images/architecture.svg)

## Timeline

| Approximate Date Range          | Description                                                                                  |
| ------------------------------- | -------------------------------------------------------------------------------------------- |
| September 15th - September 28th | Design and build frontend/backend, make with a Web API and connect a blind and oblivious bot |
| September 29th - October 26th   | Create models to play the game                                                               |
| October 27th - November 2nd     | Inter-group testing make note any fixes needed                                               |
| November 3rd - November 9th     | Implement fixes                                                                              |
| November 10th - November 16th   | Minor user testing                                                                           |
| November 17th - November 23rd   | Final polishing step to prep for final user testing                                          |
| November 24th - November 30th   | Final user testing stage - collect data to be used in presentations.                         |
| December 1st - December 20th    | Project completion - Preparation for Presentation                                            |

## Deveolopmental Resources

### People

Grant, Xavier, Sanjay, Andrew

Non-monetary Sponsor: Northrop Grumman 

### Hardware Requirements

- Either a Mac with xGB of RAM or a GPU with xGB of Ram

### Software Requirements

- Python w/ [Flask](https://flask.palletsprojects.com/en/stable/)
- HTML(+Jinja)
- CSS
- JS
- [HuggingFace](https://huggingface.co/)
- [Mistral 7B](https://mistral.ai/news/announcing-mistral-7b)
- SQLite

## How to use

As it sits currently, clone the repository, and enter the commad `flask run`

Dependancies: Python, flask, Browser(for previewing web app)

Also `flask run --host=0.0.0.0` will broadcast the app to the local network allowing other devices to connect as will be important when we want to add multi-player functionality.
