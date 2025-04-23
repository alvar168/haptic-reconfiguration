import numpy as np
import pygame
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
import pygame_widgets
from pygame.locals import KEYDOWN, K_SPACE
from typing import Optional
from datetime import datetime, timezone, timedelta
import os

from information_gain import ig_optimal, construct_saliency


def user_study_h_mapping(
    theta: np.ndarray,
    theta_perm: Optional[np.ndarray] = None,
    xdim: int = 4,
    ydim: int = 4,
    N_INTERFACES: int = 3,
):
    """
    h_mapping specific to the user study
    """
    interface_weights = [4.0, 3.0, 2.0]  # how many signals each interface can show
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


def main():
    """
    this function runs the slider code. once the user selects a preference,
    the window closes and the interface configuration selector code runs.
    it prints the optimal permutations in order from high to low, and also
    prints the corresponding information gain for each interface configuration
    """
    DONE = False
    XDIM = 4
    YDIM = 4
    BETA = 5.0
    N_INTERFACES = 3
    N_AXIS = 2

    P = 0.5 * np.eye(3)

    """EDIT LINES BELOW TO CHANGE RESOLUTION. DOING SO WILL CHANGE HOW SLIDERS LOOK"""
    XRES = 680
    YRES = 800
    """begin pygame setup"""
    pygame.init()
    win = pygame.display.set_mode((XRES, YRES))
    slider1 = Slider(win, 50, 50, 580, 50, min=0, max=10, step=1, initial=5)
    textbox1 = TextBox(win, 680 // 2 - 75, 1, 150, 50)
    textbox1.disable()
    slider2 = Slider(win, 50, 200, 580, 50, min=0, max=10, step=1, initial=5)
    textbox2 = TextBox(win, 680 // 2 - 75, 150, 150, 50)
    textbox2.disable()
    slider3 = Slider(win, 50, 350, 580, 50, min=0, max=10, step=1, initial=5)
    textbox3 = TextBox(win, 680 // 2 - 75, 300, 150, 50)
    textbox3.disable()
    output = TextBox(win, 340 - 100, 750, 200, 50)
    output.disable()
    my_event = pygame.USEREVENT + 1
    done = False
    textbox1.setText(f"Pressure:  {int(P[0, 0] * 10)}/10")
    textbox2.setText(f"Frequency: {int(P[1, 1] * 10)}/10")
    textbox3.setText(f"Area:      {int(P[2, 2] * 10)}/10")
    while not done:
        events = pygame.event.get()
        win.fill((255, 255, 255))
        for event in events:
            if event.type == pygame.QUIT:
                quit()
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    pygame.time.set_timer(my_event, 250)
                    output.setText("Calculating...")
            if event.type == my_event:
                P[0, 0] = slider1.getValue() / 10
                P[1, 1] = slider2.getValue() / 10
                P[2, 2] = slider3.getValue() / 10
                textbox1.setText(f"Pressure:  {int(P[0, 0] * 10)}/10")
                textbox2.setText(f"Frequency: {int(P[1, 1] * 10)}/10")
                textbox3.setText(f"Area:      {int(P[2, 2] * 10)}/10")
                done = True
        pygame_widgets.update(events)
        pygame.display.update()
        textbox1.setText(f"Pressure:  {int(P[0, 0] * 10)}/10")
        textbox2.setText(f"Frequency: {int(P[1, 1] * 10)}/10")
        textbox3.setText(f"Area:      {int(P[2, 2] * 10)}/10")
    W = construct_saliency(P, gamma=0.25)
    igs, perms, idxs = ig_optimal(
        W,
        xdim=XDIM,
        ydim=YDIM,
        beta=BETA,
        n_interfaces=N_INTERFACES,
        n_axis=N_AXIS,
        h_func=user_study_h_mapping,
    )
    s = "Selected Interface Configurations [Pressure Area Frequency]. 0 means X axis, 1 means Y axis, -1 means unused"
    print("=" * len(s))
    print(s)
    print("=" * len(s))
    for i in range(len(igs)):
        print(f"info gain: {np.round(igs[idxs[i]], 2):1.2f} config: {perms[idxs[i]]}")
    x = input("\nDone? [y/n] ").lower()
    pygame.quit()

    os.makedirs("data", exist_ok=True)
    with open("./data/log.log", "a") as fh:
        fh.write("=" * len(s) + "\n")
        fh.write(f"{datetime.now(timezone(timedelta(hours=-5), 'EST'))}\n")
        fh.write(f"Preferences: {P[0, 0]} {P[1, 1]} {P[2, 2]}\n")
        fh.write(f"Saliency: {W[0, 0]} {W[1, 1]} {W[2, 2]}\n")
        for i in range(len(igs)):
            fh.write(
                f"info gain: {np.round(igs[idxs[i]], 2):1.2f} config: {perms[idxs[i]]}\n"
            )

    return x == "y"


if __name__ == "__main__":
    done = False
    while not done:
        done = main()
