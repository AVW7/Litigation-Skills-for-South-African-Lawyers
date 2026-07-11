#!/usr/bin/env python3
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

OUT = os.path.dirname(os.path.abspath(__file__))
plt.rcParams.update({
    "figure.facecolor": "#1e1e1e", "axes.facecolor": "#1e1e1e",
    "savefig.facecolor": "#1e1e1e", "text.color": "#e0e0e0",
    "axes.labelcolor": "#e0e0e0", "xtick.color": "#b0b0b0",
    "ytick.color": "#b0b0b0", "axes.edgecolor": "#666666",
    "font.size": 10, "axes.titlecolor": "#e0e0e0",
})
FPS = 1
PALETTE = dict(blue="#4fc3f7", green="#66bb6a", orange="#ff7043",
               red="#ef5350", yellow="#ffca28", grey="#9e9e9e")

def save(anim, name, fps=FPS):
    p = os.path.join(OUT, name + ".gif")
    anim.save(p, writer=PillowWriter(fps=fps))
    plt.close('all')
    print("  ->", name + ".gif")

def gen_trial_timeline():
    fig, ax = plt.subplots(figsize=(6, 2.5))
    phases = ["Summons", "Pleadings", "Discovery", "Pre-Trial", "Trial", "Judgment"]
    def upd(k):
        ax.clear()
        ax.axis("off")
        ax.set_xlim(0, 18)
        ax.set_ylim(0, 2)
        ax.set_title("Civil Trial Timeline (L00-L28)")
        for idx, p in enumerate(phases[:k+1]):
            color = plt.cm.viridis(idx / 6)
            ax.add_patch(plt.Rectangle((idx * 2.8 + 0.2, 0.4), 2.4, 1.2, color=color, ec="#222"))
            ax.text(idx * 2.8 + 1.4, 1.0, p, ha="center", va="center", fontsize=8, color="#111", fontweight="bold")
            if idx > 0:
                ax.annotate("", (idx * 2.8 + 0.2, 1.0), (idx * 2.8 - 2.8 + 2.6, 1.0),
                            arrowprops=dict(arrowstyle="->", color="#888", lw=1.5))
        return []
    save(FuncAnimation(fig, upd, frames=6, blit=False), "anim_trial_timeline", fps=1)

def gen_pleadings_flow():
    fig, ax = plt.subplots(figsize=(6, 2.5))
    steps = [
        "1. Summons &\nParticulars of Claim\n(Plaintiff)",
        "2. Intention\nto Defend\n(Defendant)",
        "3. Plea &\nCounterclaim\n(Defendant)",
        "4. Replication\n(Plaintiff)",
        "5. Close of\nPleadings\n(Litis Contestatio)"
    ]
    def upd(k):
        ax.clear()
        ax.axis("off")
        ax.set_xlim(0, 15)
        ax.set_ylim(0, 2)
        ax.set_title("Exchange of Pleadings Flow (L05-L08)")
        for idx, s in enumerate(steps[:k+1]):
            color = plt.cm.cool(idx / 5)
            ax.add_patch(plt.Rectangle((idx * 2.9 + 0.2, 0.3), 2.6, 1.3, color=color, ec="#222"))
            ax.text(idx * 2.9 + 1.5, 0.95, s, ha="center", va="center", fontsize=7.5, color="#111", fontweight="bold")
            if idx > 0:
                ax.annotate("", (idx * 2.9 + 0.2, 0.95), (idx * 2.9 - 2.9 + 2.8, 0.95),
                            arrowprops=dict(arrowstyle="->", color="#888", lw=1.5))
        return []
    save(FuncAnimation(fig, upd, frames=5, blit=False), "anim_pleadings_flow", fps=1)

def gen_motion_exchange():
    fig, ax = plt.subplots(figsize=(6, 2.5))
    steps = [
        "1. Notice of Motion\n& Founding Affidavit\n(Applicant)",
        "2. Notice of\nOpposition\n(Respondent)",
        "3. Answering\nAffidavit\n(Respondent)",
        "4. Replying\nAffidavit\n(Applicant)",
        "5. Hearing &\nArgument\n(Motion Court)"
    ]
    def upd(k):
        ax.clear()
        ax.axis("off")
        ax.set_xlim(0, 15)
        ax.set_ylim(0, 2)
        ax.set_title("Motion Application Exchange (L10, L22)")
        for idx, s in enumerate(steps[:k+1]):
            color = plt.cm.spring(idx / 5)
            ax.add_patch(plt.Rectangle((idx * 2.9 + 0.2, 0.3), 2.6, 1.3, color=color, ec="#222"))
            ax.text(idx * 2.9 + 1.5, 0.95, s, ha="center", va="center", fontsize=7.5, color="#111", fontweight="bold")
            if idx > 0:
                ax.annotate("", (idx * 2.9 + 0.2, 0.95), (idx * 2.9 - 2.9 + 2.8, 0.95),
                            arrowprops=dict(arrowstyle="->", color="#888", lw=1.5))
        return []
    save(FuncAnimation(fig, upd, frames=5, blit=False), "anim_motion_exchange", fps=1)

def gen_burden_proof():
    fig, ax = plt.subplots(figsize=(5, 3))
    def upd(frame):
        ax.clear()
        ax.set_xlim(-2, 2)
        ax.set_ylim(-1, 2)
        ax.axis("off")
        
        # Draw scale stand
        ax.plot([0, 0], [0, 1.5], color=PALETTE["grey"], lw=4) # vertical pillar
        ax.plot([-1.5, 1.5], [0, 0], color=PALETTE["grey"], lw=6) # base
        
        if frame == 0:
            # Civil standard: Balance of Probabilities (51% Plaintiff)
            ax.set_title("Civil: Balance of Probabilities (51%+)", fontsize=11)
            # Crossbar tilts down on left (Plaintiff)
            ax.plot([-1.2, 1.2], [1.3, 1.7], color=PALETTE["grey"], lw=3)
            # Left pan (lower)
            ax.plot([-1.2, -1.2], [1.3, 0.7], color=PALETTE["blue"], lw=1.5)
            ax.add_patch(plt.Rectangle((-1.5, 0.5), 0.6, 0.2, color=PALETTE["blue"]))
            ax.text(-1.2, 0.2, "Plaintiff\n(51%)", ha="center", va="center", color=PALETTE["blue"], fontsize=9, fontweight="bold")
            # Right pan (higher)
            ax.plot([1.2, 1.2], [1.7, 1.1], color=PALETTE["orange"], lw=1.5)
            ax.add_patch(plt.Rectangle((0.9, 0.9), 0.6, 0.2, color=PALETTE["orange"]))
            ax.text(1.2, 0.6, "Defendant\n(49%)", ha="center", va="center", color=PALETTE["orange"], fontsize=9)
        else:
            # Criminal standard: Beyond Reasonable Doubt (99% State)
            ax.set_title("Criminal: Beyond Reasonable Doubt (99%+)", fontsize=11)
            # Crossbar tilts heavily down on left (State)
            ax.plot([-1.2, 1.2], [0.9, 2.1], color=PALETTE["grey"], lw=3)
            # Left pan (much lower)
            ax.plot([-1.2, -1.2], [0.9, 0.3], color=PALETTE["red"], lw=1.5)
            ax.add_patch(plt.Rectangle((-1.5, 0.1), 0.6, 0.2, color=PALETTE["red"]))
            ax.text(-1.2, -0.2, "State\n(99%)", ha="center", va="center", color=PALETTE["red"], fontsize=9, fontweight="bold")
            # Right pan (much higher)
            ax.plot([1.2, 1.2], [2.1, 1.5], color=PALETTE["green"], lw=1.5)
            ax.add_patch(plt.Rectangle((0.9, 1.3), 0.6, 0.2, color=PALETTE["grey"]))
            ax.text(1.2, 1.0, "Accused\n(Presumed\nInnocent)", ha="center", va="center", color=PALETTE["green"], fontsize=9)
            
        return []
    save(FuncAnimation(fig, upd, frames=2, blit=False), "anim_burden_proof", fps=0.5)

if __name__ == "__main__":
    print("Generating South African Litigation Animations...")
    gen_trial_timeline()
    gen_pleadings_flow()
    gen_motion_exchange()
    gen_burden_proof()
    print("Animations completed!")
