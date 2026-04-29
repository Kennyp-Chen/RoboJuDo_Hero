import logging
import time
from multiprocessing import Queue
from queue import Empty

from robojudo.controller import Controller, ctrl_registry
from robojudo.controller.ctrl_cfgs import UnitreeCtrlCfg
from robojudo.controller.joystick_ctrl import JoystickCtrl
from robojudo.controller.utils.joystick import unitreeRemoteController

logger = logging.getLogger(__name__)


@ctrl_registry.register
class UnitreeCtrl(JoystickCtrl):
    cfg_ctrl: UnitreeCtrlCfg

    def __init__(self, cfg_ctrl: UnitreeCtrlCfg, env=None, device="cpu"):
        # Skip JoystickCtrl initialization
        Controller.__init__(self, cfg_ctrl=cfg_ctrl, env=env, device=device)
        self.unitree_env = env

        self.state_queue = Queue(maxsize=2)  # for axes
        self.event_queue = Queue(maxsize=100)  # for button/dpad events
        self.unitree_remote_controller = unitreeRemoteController(self.state_queue, self.event_queue)

        self.axes_names = ["LeftX", "LeftY", "RightX", "RightY"]
        self.reset()

        if self.unitree_env is not None:
            self.unitree_env.RemoteControllerHandler = self.unitree_remote_controller.parse
        else:
            logger.warning("No Unitree env, controller not working.")

    def reset(self):
        self.combination_init_buttons = self.cfg_ctrl.combination_init_buttons
        self.onhold_buttons = set()
        while not self.state_queue.empty():
            try:
                self.state_queue.get_nowait()
            except Empty:
                break

        while not self.event_queue.empty():
            try:
                self.event_queue.get_nowait()
            except Empty:
                break

        self.last_state = {
            "type": "axes",
            "axes": {name: 0.0 for name in self.axes_names},
            "timestamp": time.time(),
        }

    def get_state(self):
        try:
            state = self.state_queue.get_nowait()
            self.last_state = state.copy()
        except Empty:
            state = self.last_state

        return state

    def get_events(self):
        events = []
        while not self.event_queue.empty():
            try:
                event = self.event_queue.get_nowait()
                events.append(event)
            except Empty:
                break
        return events

    def get_data(self):
        state = self.get_state()
        events = self.get_events()

        return {
            "axes": state["axes"],
            "button_event": events,
        }

    def process_triggers(self, ctrl_data):
        commands = []
        if len(self.triggers) == 0:
            return ctrl_data, commands

        for event in ctrl_data["button_event"]:
            if event["type"] == "button":
                if event["name"] in self.combination_init_buttons:
                    if event["pressed"]:
                        self.onhold_buttons.add(event["name"])
                    else:
                        self.onhold_buttons.discard(event["name"])
                else:
                    if event["pressed"]:
                        command = None
                        if len(self.onhold_buttons) == 0:
                            command = self.triggers.get(event["name"], None)
                        else:
                            event_combination = "+" .join(sorted(list(self.onhold_buttons)) + [event["name"]])
                            command = self.triggers.get(event_combination, None)
                        if command is not None:
                            commands.append(command)
                            # remove event after triggered
                            ctrl_data["button_event"].remove(event)

        return ctrl_data, commands


if __name__ == "__main__":
    from robojudo.config.g1.env.g1_real_env_cfg import G1RealEnvCfg
    from robojudo.environment.unitree_cpp_env import UnitreeCppEnv

    env = UnitreeCppEnv(G1RealEnvCfg())
    ctrl = UnitreeCtrl(cfg_ctrl=UnitreeCtrlCfg(), env=env)

    while True:
        env.update()
        print(ctrl.get_data())
        print("================================")
        time.sleep(0.1)  # Simulate a control loop
