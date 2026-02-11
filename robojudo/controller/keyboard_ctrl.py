import time
from queue import Empty, Queue

from robojudo.controller import Controller, ctrl_registry
from robojudo.controller.ctrl_cfgs import KeyboardCtrlCfg
from robojudo.controller.utils.keyboard import KeyboardThread


@ctrl_registry.register
class KeyboardCtrl(Controller):
    cfg_ctrl: KeyboardCtrlCfg

    def __init__(self, cfg_ctrl: KeyboardCtrlCfg, env=None, **kwargs):  # TODO
        super().__init__(cfg_ctrl=cfg_ctrl, env=env, **kwargs)

        self.event_queue = Queue(maxsize=100)
        self.keyboard_thread = KeyboardThread(self.event_queue)
        self.keyboard_thread.start()

        # Track pressed keys for continuous movement
        self.pressed_keys = set()
        
        # Virtual axes for keyboard movement control
        self.axes = {
            "LeftX": 0.0,    # left/right movement (a/d)
            "LeftY": 0.0,    # forward/backward movement (w/s)  
            "RightX": 0.0,   # turning (q/e)
            "RightY": 0.0,   # unused
        }

        self.reset()

    def reset(self):
        self.pressed_keys.clear()
        self.axes = {
            "LeftX": 0.0,
            "LeftY": 0.0, 
            "RightX": 0.0,
            "RightY": 0.0,
        }
        while not self.event_queue.empty():
            try:
                self.event_queue.get_nowait()
            except Empty:
                break

    def get_events(self):
        events = []
        while not self.event_queue.empty():
            try:
                event = self.event_queue.get_nowait()
                events.append(event)
            except Empty:
                break
        return events

    def update_axes(self):
        """Update virtual axes based on currently pressed keys"""
        # Reset axes
        self.axes["LeftX"] = 0.0
        self.axes["LeftY"] = 0.0
        self.axes["RightX"] = 0.0
        
        # Forward/backward (w/s)
        if "w" in self.pressed_keys:
            self.axes["LeftY"] = 1.0
        elif "s" in self.pressed_keys:
            self.axes["LeftY"] = -1.0
            
        # Left/right strafe (a/d)
        if "a" in self.pressed_keys:
            self.axes["LeftX"] = -1.0
        elif "d" in self.pressed_keys:
            self.axes["LeftX"] = 1.0
            
        # Turn left/right (q/e)
        if "q" in self.pressed_keys:
            self.axes["RightX"] = -1.0
        elif "e" in self.pressed_keys:
            self.axes["RightX"] = 1.0

    def get_data(self):
        events = self.get_events()
        
        # Update pressed keys state
        for event in events:
            if event["type"] == "keyboard":
                if event["pressed"]:
                    self.pressed_keys.add(event["name"])
                else:
                    self.pressed_keys.discard(event["name"])
        
        # Update virtual axes
        self.update_axes()
        
        return {
            "keyboard_event": events,
            "axes": self.axes.copy(),
            "button_event": [],  # Empty for compatibility with joystick interface
        }

    def process_triggers(self, ctrl_data):
        commands = []
        if len(self.triggers) == 0:
            return ctrl_data, commands

        for event in ctrl_data["keyboard_event"]:
            if event["type"] == "keyboard" and not event["pressed"]:  # trigger when key is released
                command = self.triggers.get(event["name"], None)
                if command is not None:
                    commands.append(command)
                    # remove event after triggered
                    ctrl_data["keyboard_event"].remove(event)

        return ctrl_data, commands


if __name__ == "__main__":
    kb_ctrl = KeyboardCtrl(
        cfg_ctrl=KeyboardCtrlCfg(
            triggers={
                "Key.space": "[TEST]",
                "\x01": "[CTRL_A]",
            }
        )
    )
    while True:
        data = kb_ctrl.get_data()
        ctrl_data, commands = kb_ctrl.process_triggers(data)
        if ctrl_data["keyboard_event"]:
            for e in ctrl_data["keyboard_event"]:
                print(e)
        if commands:
            print("Commands:", commands)
        print("Axes:", ctrl_data["axes"])
        time.sleep(0.1)
