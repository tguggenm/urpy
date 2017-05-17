import random
from collections import namedtuple
from enum import Enum
import attr


class IllegalMove(Exception): ...


class Field(namedtuple('Field', ('war', 'rosette', 'go_again', 'token'))):

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


def can_move_to(player, field):
    return field.empty() or (field.owned_by_opponent(player) and not field.rosette)


@attr.s
class Track:

    tokens = attr.ib(default=[Tokens.EMPTY] * 14)
    bench = attr.ib(default=7)
    home = attr.ib(default=0)
    bench_opp = attr.ib(default=7)
    home_opp = attr.ib(default=0)
    player = attr.ib(default=Tokens.P1)


    def __len__(self):
        return len(self.tokens)

    def __getitem__(self, idx):
        token = self.tokens[idx]
        return Field(war=(idx in range(4, 12)),
                     rosette=(idx in (3, 7, 13)),
                     go_again=(idx == 3),
                     token=token)

    @property
    def own_fields(self):
        return (i for (i, fld) in enumerate(self) if fld.owned_by(self.player))


    def apply_move(self, player, mv):
        if player == self.player:
            if mv.src is None:
                self.bench -= 1
            if mv.dst is None:
                self.home += 1
            if self[mv.dst].owned_by_opponent(player):
                self.bench_opp += 1
                self.tokens[dst] = player
        else:
            if mv.src is None:
                self.bench_opp -= 1
            if mv.dst is None:
                self.home_opp += 1
            if self[mv.dst].owned_by_opponent(player):
                self.bench += 1
                self.tokens[dst] = player


Move = namedtuple('Move', ('src', 'dst'))


def get_moves(track, roll):
    if roll == 0:
        return set()

    pawns = {idx for idx in track.own_fields
             if idx + roll < len(track) + 1}

    remain = {idx for idx in pawns if idx + roll < len(track)}
    leave = pawns - remain

    remain_legal = {idx for idx in remain if can_move_to(track.player, track[idx + roll])}
    can_enter = track.bench > 0 and can_move_to(track.player, track[roll - 1])

    moves = {Move(src=idx, dst=idx + roll) for idx in remain_legal}
    moves |= {Move(src=idx, dst=None) for idx in leave}
    if can_enter:
        moves.add(Move(src=None, dst=roll - 1))

    return moves


tr = Track()
moves = get_moves(tr, 2)
print(moves)
