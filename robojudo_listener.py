#!/usr/bin/env python3
"""
使用robojudo相同架构的G1手柄控制器
通过Unitree机器人获取手柄数据，与run_pipeline_serv.py使用相同的机制
"""

import os
import sys
import time
import subprocess
import signal
import psutil
import logging
import struct
from threading import Thread

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gamepad_listener.log', mode='w'),  # mode='w' 每次重启清空日志
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 配置
WORK_DIR = os.path.expanduser("~/chenyupeng/sim2real/RoboJuDo")
CONDA_ENV = "robojudo"
SCRIPT_PATH = "scripts/run_pipline_real.py"
LOG_FILE = "run.log"

# 切换工作目录
os.chdir(WORK_DIR)

# 全局状态
is_running_task = False
task_process = None
current_pressed_buttons = set()
stop_listener = False

# Unitree手柄按键映射 (参考robojudo的实现)
button_map = [
    "R1",
    "L1", 
    "Start",
    "Select",
    "R2",
    "L2",
    "F1",
    "F2",
    "A",
    "B",
    "X",
    "Y",
    "Up",
    "Right",
    "Down",
    "Left",
]

class UnitreeGamepadHandler:
    """Unitree手柄数据处理器，参考robojudo的实现"""
    
    def __init__(self):
        self.last_button_state = [0] * 16
        
    def parse(self, remote_data):
        """解析Unitree手柄数据 (参考robojudo joystick.py中的unitreeRemoteController)"""
        global current_pressed_buttons
        
        try:
            # 解析按键数据 (与robojudo相同的解析方式)
            keys = struct.unpack("H", remote_data[2:4])[0]
            button = [((keys & (1 << i)) >> i) for i in range(16)]
            button_state = [int(b) for b in button]
            
            # 更新当前按下的按键
            current_pressed_buttons.clear()
            for i in range(16):
                if button_state[i]:
                    btn_name = button_map[i]
                    current_pressed_buttons.add(btn_name)
                    
            # 检查按键变化并记录
            changed = [button_state[i] != self.last_button_state[i] for i in range(16)]
            for i in range(16):
                if changed[i] and button_state[i] == 1:
                    btn_name = button_map[i]
                    logger.debug(f"按键按下: {btn_name}")
                    
                    # 检查组合按键
                    check_combinations()
            
            # 更新状态
            self.last_button_state = button_state
            
        except Exception as e:
            logger.error(f"解析手柄数据失败: {e}")

def check_combinations():
    """检查组合按键"""
    global current_pressed_buttons, is_running_task
    
    logger.debug(f"当前按键: {current_pressed_buttons}")
    
    # L1 + R1 + A
    if {"L1", "R1", "A"}.issubset(current_pressed_buttons):
        if not is_running_task:
            logger.info("检测到 L1+R1+A，启动任务")
            start_task()
    
    # L1 + R1 + B
    if {"L1", "R1", "B"}.issubset(current_pressed_buttons):
        logger.info("检测到 L1+R1+B，停止监听并交还控制权给PC1")
        stop_self_and_handover_to_pc1()
        global stop_listener
        stop_listener = True

def is_process_running(pid):
    """检查进程是否运行"""
    try:
        return psutil.pid_exists(pid)
    except:
        return False

def start_task():
    """启动任务脚本"""
    global is_running_task, task_process
    if is_running_task:
        return

    logger.info("启动任务脚本...")

    try:
        # 启动命令：使用conda run确保环境正确
        full_cmd = "conda run -n robojudo nohup python scripts/run_pipline_real.py > run.log 2>&1 & echo $!"
        result = subprocess.check_output(full_cmd, shell=True, text=True)
        pid = int(result.strip())

        task_process = pid
        is_running_task = True
        logger.info(f"任务已启动，PID={pid}")
        
    except Exception as e:
        logger.error(f"启动任务失败: {e}")
        is_running_task = False
        task_process = None

def stop_self_and_handover_to_pc1():
    """停止监听并交还控制权给PC1"""
    global stop_listener
    
    logger.info("收到交还控制权指令，停止systemd服务...")
    
    try:
        # 方法1：尝试使用systemctl --user（如果配置了用户级服务）
        result = subprocess.run("systemctl --user stop gamepad_listener 2>/dev/null", shell=True)
        if result.returncode == 0:
            logger.info("已通过用户级服务停止监听，控制权交还给PC1")
            return
        
        # 方法2：尝试使用sudo（如果配置了免密）
        result = subprocess.run("sudo -n systemctl stop gamepad_listener 2>/dev/null", shell=True)
        if result.returncode == 0:
            logger.info("已通过系统级服务停止监听，控制权交还给PC1")
            return
        
        # 方法3：如果都失败了，记录错误并退出
        logger.error("无法停止systemd服务，请检查权限配置")
        logger.info("尝试的解决方案：")
        logger.info("1. 配置用户级服务：systemctl --user enable gamepad_listener")
        logger.info("2. 配置sudo免密：sudo visudo 添加 NOPASSWD 配置")
        
        # 备用方案：正常退出
        stop_listener = True
        
    except Exception as e:
        logger.error(f"停止服务失败: {e}")
        stop_listener = True



def init_unitree_connection():
    """初始化与Unitree机器人的连接 (使用与robojudo相同的方式)"""
    try:
        logger.info("正在连接Unitree机器人...")
        
        # 导入robojudo的模块 (修复导入路径)
        from robojudo.environment.unitree_cpp_env import UnitreeCppEnv
        from robojudo.config.g1.g1_cfg import G1UnitreeCfg
        from robojudo.config.g1.env.g1_real_env_cfg import G1RealEnvCfg
        
        # 创建与g1_real_locomimic相同的配置
        env_cfg = G1RealEnvCfg(
            env_type="UnitreeCppEnv",
            unitree=G1UnitreeCfg(net_if="eth0"),
        )
        
        # 创建环境
        env = UnitreeCppEnv(env_cfg)
        
        # 设置手柄数据处理器 (与robojudo相同的方式)
        gamepad_handler = UnitreeGamepadHandler()
        env.RemoteControllerHandler = gamepad_handler.parse
        
        logger.info("Unitree机器人连接成功")
        return env
        
    except Exception as e:
        logger.error(f"连接Unitree机器人失败: {e}")
        logger.info("请确保:")
        logger.info("1. 机器人已开机并连接到网络")
        logger.info("2. 网络接口配置正确 (eth0)")
        logger.info("3. unitree_cpp模块已正确安装")
        logger.info("4. robojudo环境已正确配置")
        return None

def main():
    """主函数"""
    global is_running_task, task_process, stop_listener
    
    logger.info("="*60)
    logger.info("G1 PC2 手柄监听已启动 (RoboJuDo模式)")
    logger.info("[🎮] L1 + R1 + A = 启动任务")
    logger.info("[🎮] L1 + R1 + B = 停止监听，交还控制权给PC1")
    logger.info("="*60)

    # 初始化状态
    is_running_task = False
    task_process = None
    current_pressed_buttons.clear()
    stop_listener = False

    # 初始化Unitree连接
    unitree_env = init_unitree_connection()
    if unitree_env is None:
        logger.error("无法连接到Unitree机器人，退出程序")
        return
    
    try:
        logger.info("开始监听手柄数据...")
        
        while not stop_listener:
            # 任务运行中：只监控进程
            if is_running_task:
                if not is_process_running(task_process):
                    logger.warning("任务已终止，恢复手柄监听")
                    is_running_task = False
                    task_process = None
                time.sleep(1)
                continue

            # 更新Unitree环境 (这会触发手柄数据解析)
            try:
                unitree_env.update()
            except Exception as e:
                logger.error(f"更新Unitree环境失败: {e}")
                time.sleep(0.1)

            time.sleep(0.02)  # 50Hz

    except KeyboardInterrupt:
        logger.info("收到中断信号，退出程序")
    except Exception as e:
        logger.error(f"程序异常: {e}")
    finally:
        # 清理资源
        try:
            if unitree_env:
                unitree_env.shutdown()
        except:
            pass
        logger.info("程序已退出")

if __name__ == "__main__":
    main()
