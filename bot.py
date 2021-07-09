import os
import sys
import threading
import random

import berserk
from dotenv import load_dotenv
import chess

load_dotenv()

session = berserk.TokenSession(os.environ.get("API_TOKEN", None))
client = berserk.Client(session=session)
print("random-lichess by cyrus yip")
username = client.account.get()["username"]
print("Connected as", username + "!")


class Game(threading.Thread):
    def __init__(self, client, game_id, **kwargs):
        super().__init__(**kwargs)
        self.game_id = game_id
        self.client = client
        self.stream = client.bots.stream_game_state(game_id)
        self.board = chess.Board()
        self.greetings = [
            "Can you beat Grandmaster Random?",
            "Although I'm a grandmaster, you should go easy on me.",
            "hi",
            "test string",
            "How brave of you to challenge me!",
            "jonathan was here",
            "justin doesn't suck",
            "This is the game of the second!",
            "Give it your all!",
            "e",
            "Good luck and have fun.",
            "Fine, I'll go easy this time.",
            "Sometimes good moves look random, you just have to look deeper.",
            '"Every chess master was once a beginner." – Irving Chernev',
            '"I don’t believe in psychology. I believe in good moves." – Bobby Fischer',
            '"Nobody ever won a chess game by resigning." – Savielly Tartakower',
            '"The pin is mightier than the sword." – Fred Reinfeld',
            "Just believe in yourself, you can do it!",
            "jayme is cool (i was forced to write this, he actually is less than cool)",
        ]
        self.adjectives = [
            "GOOD",
            "GREAT",
            "EXCELLENT",
            "AMAZING",
            "BRILLIANT",
            "WONDERFUL",
            "RIVETING",
            "TERRIFIC",
            "NOT BAD",
            "DELICIOUS",
            "MARVELOUS",
            "ADMIRABLE",
            "SCRUMPTIOUS",
            "SUCCULENT",
            "WICKED",
            "TREMENDOUS",
            "YUMMY"
        ]

    def move(self):
        move = random.choice(list(self.board.generate_legal_moves()))
        self.board.push(move)
        self.client.bots.make_move(self.game_id, move.uci())

    def run(self):
        for event in self.stream:
            print(event)
            if event["type"] == "gameState":
                if event["status"] != "started":
                    self.client.bots.post_message(
                        self.game_id,
                        random.choice(self.adjectives) + " game, well played.",
                    )
                    sys.exit()
                try:
                    self.board.push_uci(event["moves"].split(" ")[-1])
                except ValueError:
                    continue
                self.move()
            elif event["type"] == "gameFull":
                self.client.bots.post_message(
                    self.game_id, random.choice(self.greetings)
                )
                if event["white"]["id"] == username.lower():
                    self.move()
                if event["initialFen"] != "startpos":
                    self.board.set_fen(event["initialFen"])
            elif event["type"] == "gameFinish":
                sys.exit()


for event in client.bots.stream_incoming_events():
    print(event)
    if event["type"] == "challenge":
        if event["challenge"]["challenger"]["id"] == username.lower():
            continue
        if (
            event["challenge"]["variant"]["key"] == "standard"
            or event["challenge"]["variant"]["key"] == "fromPosition"
            and event["challenge"]["rated"] is False
            and event["challenge"]["speed"] != "correspondence"
        ):
            client.bots.accept_challenge(event["challenge"]["id"])
        else:
            client.bots.decline_challenge(event["challenge"]["id"])
    elif event["type"] == "gameStart":
        game = Game(client, event["game"]["id"])
        game.start()
