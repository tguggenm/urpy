import random
from collections import namedtuple
from enum import Enum
import attr


class IllegalMove(Exception): ...


class Field(namedtuple('Field', ('war', 'rosette', 'token'))):

    def __bool__(self):
        return self.token != Tokens.EMPTY

    def empty(self):
        return not bool(self)

    def owned_by(self, player):
        return self.token == player

    def owned_by_opponent(self, player):
        return self and not self.owned_by(player)


class Tokens(Enum):
    EMPTY, P1, P2 = 0, 1, 2

def opponent(player):
    if player == Tokens.P1:
        return Tokens.P2
    elif player == Tokens.P2:
        return Tokens.P1
    else:
        raise ValueError

def can_move_to(player, field):
    return field.empty() or (field.owned_by(opponent(player)) and not field.rosette)


@attr.s
class Track:

    tokens = attr.ib(default=[Tokens.EMPTY] * 14)
    bench = attr.ib(default={p: 7 for p in (Tokens.P1, Tokens.P2)})
    home = attr.ib(default={p: 0 for p in (Tokens.P1, Tokens.P2)})

    def __len__(self):
        return len(self.tokens)

    def __getitem__(self, idx):
        token = self.tokens[idx]
        return Field(war=(idx in range(4, 12)),
                     rosette=(idx in (3, 7, 13)),
                     token=token)

    @property
    def owned_fields(self, player):
        return (i for (i, fld) in enumerate(self) if fld.owned_by(player))

    # def apply_move(self, player, mv):



Move = namedtuple('Move', ('src', 'dst'))


def get_moves(track, player, roll):
    if roll == 0:
        return set()

    pawns = {idx for idx in track.owned_fields(player)
             if idx + roll < len(track) + 1}

    remain = {idx for idx in pawns if idx + roll < len(track)}
    leave = pawns - remain
    remain = {idx for idx in remain if can_move_to(player, track[idx + roll])}
    can_enter = track.bench[player] > 0 and can_move_to(player, track[roll - 1])

    moves = {Move(src=idx, dst=idx + roll) for idx in remain}
    moves |= {Move(src=idx, dst=None) for idx in leave}
    if can_enter:
        moves.add(Move(src=None, dst=roll - 1))

    return moves


tr = Track()
