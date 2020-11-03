from .task import Task

class MaximizeContinuousProgressTask(Task):
  def __init__(self, laps: int, time_limit: float, terminate_on_collision: bool,
               collision_reward: float = -25, frame_reward: float = -0.025, progress_factor: float = +100):
    self._laps = laps
    self._time_limit = time_limit
    self._terminate_on_collision = terminate_on_collision
    self._last_progress = None
    self._collision_reward = collision_reward
    self._frame_reward = frame_reward
    self._progress_factor = progress_factor

  def reward(self, agent_id, state, action) -> float:
    agent_state = state[agent_id]
    progress = agent_state['lap'] + agent_state['progress']
    if self._last_progress is None:
      self._last_progress = progress
    delta = progress - self._last_progress
    if delta > .5:  # the agent is crossing the starting line in the wrong direction
      delta = -delta
    reward = self._frame_reward
    collision = agent_state['wall_collision'] or len(agent_state['opponent_collisions']) > 0
    if collision:
      reward += self._collision_reward
    else:
      reward += self._progress_factor * delta
      self._last_progress = progress
    return reward

  def done(self, agent_id, state) -> bool:
    agent_state = state[agent_id]
    collision = agent_state['wall_collision'] or len(agent_state['opponent_collisions']) > 0
    if self._terminate_on_collision and collision:
      return True
    return agent_state['lap'] > self._laps or self._time_limit < agent_state['time']

  def reset(self):
    self._last_progress = None


class MaximizeProgressTask(Task):
    def __init__(self, laps: int, time_limit: float, terminate_on_collision: bool,
                 delta_progress=0.001, collision_reward=-100, frame_reward=-0.1, progress_reward=1):
        self._time_limit = time_limit
        self._laps = laps
        self._terminate_on_collision = terminate_on_collision
        self._last_stored_progress = None
        # reward params
        self._delta_progress = delta_progress
        self._progress_reward = progress_reward
        self._collision_reward = collision_reward
        self._frame_reward = frame_reward


    def reward(self, agent_id, state, action) -> float:
        agent_state = state[agent_id]
        progress = agent_state['lap'] + agent_state['progress']
        if self._last_stored_progress is None:
            self._last_stored_progress = progress
        delta = progress - self._last_stored_progress
        reward = self._frame_reward
        collision = agent_state['wall_collision'] or len(agent_state['opponent_collisions']) > 0
        if collision == True:
            reward += self._collision_reward
        reward += delta * 10.0
        self._last_stored_progress = progress
        return reward

    def done(self, agent_id, state) -> bool:
        agent_state = state[agent_id]
        collision = agent_state['wall_collision'] or len(agent_state['opponent_collisions']) > 0
        if self._terminate_on_collision and collision:
            return True
        return agent_state['lap'] > self._laps or self._time_limit < agent_state['time']

    def reset(self):
        self._last_stored_progress = None


class RankDiscountedMaximizeProgressTask(MaximizeProgressTask):

    def __init__(self, laps: int, time_limit: float, terminate_on_collision: bool, delta_progress=0.001,
                 collision_reward=-100, frame_reward=-0.1, progress_reward=1):
        super().__init__(laps, time_limit, terminate_on_collision, delta_progress, collision_reward, frame_reward,
                         progress_reward)

    def reward(self, agent_id, state, action) -> float:
        rank = state[agent_id]['rank']
        reward = super().reward(agent_id, state, action)
        reward = reward / float(rank)
        return reward
