from typing import Callable
import numpy as np
from itertools import product


def h_mapping(
    theta: np.ndarray,
    theta_perm: np.ndarray | None = None,
    xdim: int = 5,
    ydim: int = 5,
):
    """
    @param theta_perm : array of -1, 0, 1. -1 means unused, 0 means xaxis, 1 means yaxis
    """
    N_INTERFACES = 3
    interface_weights = [5.0, 3.0, 2.0]
    if theta_perm is None:
        theta_perm = np.array([0, 1, 1])
    assert len(theta_perm) == N_INTERFACES, "theta_perm must match n_interfaces"
    signal_dim = len(np.where(theta_perm >= 0)[0])
    signal_idx = 0
    signal = np.empty(signal_dim)
    for i in range(N_INTERFACES):
        if theta_perm[i] == -1:
            continue
        elif theta_perm[i] == 0:
            signal[signal_idx] = np.floor(theta[0] * interface_weights[i] / xdim)
        elif theta_perm[i] == 1:
            signal[signal_idx] = np.floor(theta[1] * interface_weights[i] / ydim)
        else:
            raise NotImplementedError(f"Theta_perm[{i}] not -1, 0, 1: {theta_perm[i]}")
        signal_idx += 1
    return signal


def human_model(
    signal: np.ndarray,
    THETAS: np.ndarray,
    W: np.ndarray,
    beta: float = 5.0,
    theta_perm: np.ndarray | None = None,
    xdim: int = 5,
    ydim: int = 5,
    h_func: Callable | None = None,
):
    """
    note that W is the full saliency matrix. if
    len(signal) is less than len(W), then we
    need to adjust the saliency matrix to scale
    with theta_perm
    """
    if h_func is None:
        h_func = h_mapping
    aug_W = W.copy()
    if len(signal) != len(W) and theta_perm is not None:
        idxs = np.where(theta_perm >= 0)[0]
        aug_W = aug_W[idxs].T[idxs]
    P = np.empty(len(THETAS))
    for idx, theta in enumerate(THETAS):
        h = h_func(theta, theta_perm=theta_perm, xdim=xdim, ydim=ydim)
        dist = (h - signal).T @ aug_W @ (h - signal)
        P[idx] = np.exp(-beta * dist**2)
    return P / np.sum(P)


def information_gain(
    SIGNALS: np.ndarray,
    THETAS: np.ndarray,
    W: np.ndarray,
    beta: float = 5.0,
    theta_perm: np.ndarray | None = None,
    xdim: int = 5,
    ydim: int = 5,
    h_func: Callable | None = None,
):
    ig = 0.0
    M = len(SIGNALS)
    L = len(THETAS)
    for idx in range(L):
        P_den = 0.0
        for s in SIGNALS:
            P_den += human_model(
                s,
                THETAS,
                W,
                beta=beta,
                theta_perm=theta_perm,
                xdim=xdim,
                ydim=ydim,
                h_func=h_func,
            )[idx]
        for s in SIGNALS:
            P_num = human_model(
                s,
                THETAS,
                W,
                beta=beta,
                theta_perm=theta_perm,
                xdim=xdim,
                ydim=ydim,
                h_func=h_func,
            )[idx]
            if P_den > 0.0 and P_num > 0.0:
                ig += P_num * np.log2(M * P_num / P_den)
    return ig / M


def construct_saliency(P: np.ndarray, gamma: float = 1.0):
    """
    @param P : preferences matrix, scaled from 0.0 to 1.0
    """
    W = (np.eye(len(P)) * gamma + P) / (1.0 + gamma)
    return W


def ig_optimal(
    W: np.ndarray,
    xdim: int = 5,
    ydim: int = 5,
    beta: float = 5.0,
    n_interfaces=3,
    n_axis=2,
    h_func: Callable | None = None,
):
    if h_func is None:
        h_func = h_mapping
    perms = np.array(list(product(np.arange(-1, n_axis), repeat=n_interfaces)))[
        1:
    ]  # remove null
    """remove reflective symmetry"""
    idx = 0
    while idx < len(perms):
        p = perms[idx]
        inv_p = (n_axis - 1) - p * (p >= 0) - (n_axis) * (p < 0)
        perms = perms[~np.all(perms == inv_p, axis=1), :]
        idx += 1

    igs = np.empty(len(perms))
    for perm_idx, perm in enumerate(perms):
        x = np.arange(0, xdim, 1)
        y = np.arange(0, ydim, 1)
        X, Y = np.meshgrid(x, y)
        THETAS = np.array([X.flatten(), Y.flatten()]).T
        L = len(THETAS)
        SIGNALS = np.empty((L, len(np.where(perm >= 0)[0])))
        for idx, theta in enumerate(THETAS):
            SIGNALS[idx] = h_func(theta, theta_perm=perm, xdim=xdim, ydim=ydim)
        igs[perm_idx] = information_gain(
            SIGNALS, THETAS, W, beta, perm, h_func=h_func, xdim=xdim, ydim=ydim
        )
    idxs = list(np.arange(len(perms)))
    idxs.sort(key=lambda idx: igs[idx], reverse=True)  # type: ignore
    return igs, perms, idxs


if __name__ == "__main__":
    print("you probably meant to run slider.py :)")
