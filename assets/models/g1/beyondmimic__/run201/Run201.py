import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.absolute()))

from FSM.FSMState import FSMStateName
from common.ctrlcomp import StateAndCmd, PolicyOutput
from policy.motion_tracking_base import MotionTrackingPolicy
import os


class Run201(MotionTrackingPolicy):
    def __init__(self, state_cmd: StateAndCmd, policy_output: PolicyOutput):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        super().__init__(
            state_cmd=state_cmd,
            policy_output=policy_output,
            policy_name=FSMStateName.SKILL_Run201,
            policy_name_str="skill_run201",
            config_file="Run201.yaml",
            policy_dir=current_dir
        )
