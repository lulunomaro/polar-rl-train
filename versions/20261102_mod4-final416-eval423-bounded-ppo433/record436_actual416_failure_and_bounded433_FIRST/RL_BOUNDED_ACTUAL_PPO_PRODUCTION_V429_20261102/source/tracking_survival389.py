"""Soft approximation of actual .75rad orientation termination, no plant change."""
import math,torch
def matched_survival389(state):
    return torch.sigmoid((state[1][...,2,2]-math.cos(.75))/.025)
