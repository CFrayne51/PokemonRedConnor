import logging

class RewardSystem:
    def __init__(self, memory, config):
        self.memory = memory
        self.config = config
        self.reward_scale = config.get("reward_scale", 1)
        
        # State tracking
        self.total_healing_rew = 0
        self.last_health = 1
        self.died_count = 0
        self.last_own_hp = 1.0
        self.last_enemy_hp = 1.0
        self.total_reward = 0.0
        self.cumulative_enemy_dmg = 0.0

    def reset(self):
        self.total_healing_rew = 0
        self.last_health = 1
        self.died_count = 0
        self.last_own_hp = self.memory.read_hp_fraction()
        self.last_enemy_hp = self.memory.read_enemy_hp_fraction()
        self.cumulative_enemy_dmg = 0.0
        self.total_reward = 0.0
        
        self.prev_party_size = self.memory.read_party_size()
        
        # Initial reward calculation to set baseline
        self.progress_reward = self.get_game_state_reward(0, 1000)
        self.total_reward = sum(self.progress_reward.values())

    def update_reward(self, step_count, max_steps):
        # Update internal state first
        self._update_internal_state()

        # Compute reward
        self.progress_reward = self.get_game_state_reward(step_count, max_steps)
        new_total = sum(self.progress_reward.values())
        step_reward = new_total - self.total_reward
        self.total_reward = new_total
        return step_reward

    def _update_internal_state(self):
        # Healing reward update
        cur_health = self.memory.read_hp_fraction()
        party_size = self.memory.read_party_size()
        
        # Initialize prev_party_size if strictly necessary, though reset() should handle it.
        if not hasattr(self, 'prev_party_size'):
             self.prev_party_size = party_size

        if cur_health > self.last_health and party_size == self.prev_party_size:
            if self.last_health > 0:
                heal_amount = cur_health - self.last_health
                self.total_healing_rew += heal_amount * heal_amount
            else:
                self.died_count += 1
        
        self.last_health = cur_health
        self.prev_party_size = party_size

    def get_game_state_reward(self, step_count, max_steps):
        # Use total-party HP fractions
        own_frac = self.memory.read_hp_fraction()
        enemy_frac = self.memory.read_enemy_hp_fraction()

        # Fractional damage since last step
        dmg_this_step = max(0.0, self.last_enemy_hp - enemy_frac)
        self.cumulative_enemy_dmg += dmg_this_step

        # Convert fractional damage to reward
        dmg_scale = 100.0
        heal_bonus = self.total_healing_rew * 5.0

        shaped = (dmg_scale * self.cumulative_enemy_dmg + heal_bonus)

        is_timeout = (step_count >= max_steps - 1)
        if not is_timeout:
            if enemy_frac <= 0.0:
                shaped += 100.0
            if own_frac <= 0.0:
                shaped -= 100.0
        else:
            shaped -= 150.0

        # Update last values
        self.last_own_hp = own_frac
        self.last_enemy_hp = enemy_frac

        return {
            "battle_reward": self.reward_scale * shaped,
            "heal": self.reward_scale * heal_bonus,
            "event": 0.0,
        }
