from stable_baselines3.common.callbacks import BaseCallback
import numpy as np
import json
from pathlib import Path
from datetime import datetime

class GlobalEpisodeLogger(BaseCallback):

    def __init__(self, num_envs, save_path, verbose=0):
        super().__init__(verbose)
        self.num_envs = num_envs

        self.current_ep = 1
        self.ep_rewards = np.zeros(num_envs)
        self.ep_lens = np.zeros(num_envs)
        self.ep_wins = np.zeros(num_envs)
        self.ep_losses = np.zeros(num_envs)

        self.done_flags = np.zeros(num_envs, dtype=bool)

        self.save_file = Path(save_path) / "episode_summaries.jsonl"
        self.save_file.parent.mkdir(exist_ok=True)
        if not self.save_file.exists():
            self.save_file.touch()

    def _on_step(self):
        infos = self.locals["infos"]  # list of dicts from each env

        for i, info in enumerate(infos):
            if "episode" in info:
                ep = info["episode"]
                self.ep_rewards[i] = ep.get("r", 0.0)
                self.ep_lens[i] = ep.get("l", 0)
                # Check for win/loss in episode or top-level info
                self.ep_wins[i] = ep.get("w", info.get("win", 0))
                self.ep_losses[i] = ep.get("loss", info.get("loss", 0))
                self.done_flags[i] = True
            elif info.get("win") or info.get("loss"):
                # Fallback for when info is present but 'episode' isn't yet (if ever)
                self.ep_wins[i] = info.get("win", 0)
                self.ep_losses[i] = info.get("loss", 0)
                # Note: we don't have r/l here without the wrapper

        # If ALL envs finished their episode, aggregate
        if self.done_flags.all():

            entry = {
                "global_episode": self.current_ep,
                "mean_reward": float(self.ep_rewards.mean()),
                "mean_length": float(self.ep_lens.mean()),
                "wins": int(self.ep_wins.sum()),
                "losses": int(self.ep_losses.sum()),
                "timestamp": datetime.now().isoformat()
            }

            with open(self.save_file, "a") as f:
                f.write(json.dumps(entry) + "\n")

            print(f"[GLOBAL EP {self.current_ep}] logged summary")

            # prepare next global episode
            self.current_ep += 1
            self.done_flags[:] = False

        return True
