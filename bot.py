import os
import sys
import threading
import random
import time

import berserk
import berserk.exceptions
from dotenv import load_dotenv
import chess

import clients

load_dotenv()

session = berserk.TokenSession(os.environ.get("API_TOKEN", None))
client = clients.Client(session=session)
print("random-lichess by cyrus yip")
username = client.account.get()["username"]
print("Connected as", username + "!")


class Game(threading.Thread):
    def __init__(self, client: clients.Client, game_id, **kwargs):
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
            "Let's try our hardest, okay?",
            '"When you see a good move, look for a better one." - Emanuel Lasker',
            "It's okay, you'll win soon enough.",
            "No hard feelings, okay?",
            "Let me tell you a secret... I'm not actually a grandmaster... Don't tell anyone!",
            "Chess is too easy.",
            "Rolling a die: " + str(random.randint(1, 6)),
            "I have a " + str(random.randint(1, 99)) + "% chance of winning.",
            '"If you are allergic to a thing, it is best not to put that thing in your mouth, particularly if the thing is cats." - Lemony Snicket',
            "Good luck. Not that it'll help...",
            "no i don't",
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
            "YUMMY",
        ]
        self.white = False

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
                    if "winner" not in event:
                        msg = "That was tough one, shame it ended in a draw."
                    elif (event["winner"] == "white") == self.white:
                        msg = "Another nice and clean win."
                    else:
                        msg = "What a tough opponent, got me with a rare defeat."
                    self.client.bots.post_message(
                        self.game_id, msg + " Have fun in analysis!", True,
                    )
                    sys.exit()
                try:
                    self.board.push_uci(event["moves"].split(" ")[-1])
                except ValueError:
                    continue
                if self.board.turn == self.white:
                    self.move()
            elif event["type"] == "gameFull":
                self.client.bots.post_message(
                    self.game_id, random.choice(self.greetings)
                )
                if event["white"].get("id", None) == username.lower():
                    self.white = True
                    self.move()
                if event["variant"]["key"] == "chess960":
                    self.board.chess960 = True
                if event["initialFen"] != "startpos":
                    self.board.set_fen(event["initialFen"])


class AutoChallenge(threading.Thread):
    def __init__(self, client: clients.Client):
        super().__init__()
        self.client = client
        self.bots = [
            "Boris-Trapsky",
            "TinezzBot_v2",
            "PlayChessTonight",
            "LeelaStrength",
            "Flagfish",
            "simpleEval",
            "FlamingDragon_9000",
            "GarboBot",
            "MiniHuman",
            "WeiaWaga",
            "WorstFish",
            "WeirdChessBot",
            "CaptureBot",
            "TuksuBot",
            "ResoluteBot",
            "bot_adario",
            "Nakshatra3",
            "RootEngine",
            "XXIstCentury"
        ]

    def run(self):
        while True:
            try:
                self.client.challenges.create(random.choice(self.bots), False, 180, 0)
            except berserk.exceptions.ResponseError as e:
                print(e)
            time.sleep(3600)


AutoChallenge(client).start()
for event in client.bots.stream_incoming_events():
    print(event)
    if event["type"] == "challenge":
        if event["challenge"]["challenger"]["id"] == username.lower():
            continue
        if not (
            event["challenge"]["variant"]["key"] == "standard"
            or event["challenge"]["variant"]["key"] == "fromPosition"
            or event["challenge"]["variant"]["key"] == "chess960"
        ):
            reason = "variant"
        elif event["challenge"]["rated"] is True:
            reason = "casual"
        elif event["challenge"]["speed"] == "correspondence":
            reason = "tooSlow"
        else:
            client.bots.accept_challenge(event["challenge"]["id"])
            continue
        client.bots.decline_challenge(event["challenge"]["id"], reason)
    elif event["type"] == "gameStart":
        game = Game(client, event["game"]["id"])
        game.start()
