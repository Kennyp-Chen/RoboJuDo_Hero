# Fix OMP perfmance issue on ARM platform (Jetson)
import os
import platform

if platform.machine().startswith("aarch64"):
    os.environ["OMP_NUM_THREADS"] = "1"

import argparse
import logging
import time

import robojudo.pipeline
from robojudo.config.config_manager import ConfigManager
from robojudo.pipeline.pipeline_cfgs import RlPipelineCfg
from robojudo.pipeline.rl_pipeline import RlPipeline

logger = logging.getLogger("robojudo")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="g1_real_locomimic",
        help="Name of the config class to use",
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    logger.info(f"Using config: {args.config}")
    config_manager = ConfigManager(config_name=args.config)

    cfg: RlPipelineCfg = config_manager.get_cfg()

    pipeline_type = cfg.pipeline_type

    pipeline_class: type[RlPipeline] = getattr(robojudo.pipeline, pipeline_type)
    logger.info(f"Using pipeline: {pipeline_type} -> {pipeline_class}")

    pipeline = pipeline_class(cfg=cfg)

    # For real robot, automatically execute prepare with sitting pose
    if not cfg.env.is_sim:
        logger.warning("=" * 60)
        logger.warning("REAL ROBOT MODE")
        logger.warning("=" * 60)
        logger.warning("Automatically starting PREPARE (move to sitting position)...")
        logger.warning("=" * 60)
        
        # Automatically run prepare (will use sitting pose from config)
        pipeline.prepare(traj_len=300)
        
        # Prepare complete, ready for control via keyboard or controller
        logger.warning("=" * 60)
        logger.warning("PREPARE COMPLETE - Robot at sitting position")
        logger.warning("=" * 60)
        logger.warning("Ready for control via keyboard or controller")
        logger.warning("Press ESC or Ctrl+C to exit")
        logger.warning("=" * 60)

    try:
        logger.warning("=" * 60)
        logger.warning("POLICY EXECUTION STARTED")
        logger.warning("Press ESC to emergency stop")
        logger.warning("=" * 60)
        
        while True:
            time_start = time.time()
            pipeline.step()
            time_end = time.time()
            time_diff = time_end - time_start

            # keep the pipeline running at the desired frequency
            if not cfg.run_fullspeed:
                time_diff = pipeline.dt - time_diff
                if time_diff > 0:
                    time.sleep(time_diff)
                else:
                    if not cfg.env.is_sim:
                        logger.error(f"Warning: frame drop -> {time_diff}")
                        # if time_diff < -0.2:
                        #     logger.critical("Exiting due to excessive frame drop")
                        #     pipeline.env.shutdown()
                        #     time.sleep(10)
                        #     break
    except KeyboardInterrupt:
        logger.warning("Keyboard interrupt received, shutting down...")
        if hasattr(pipeline, 'env'):
            pipeline.env.shutdown()
        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        # Ensure terminal is restored
        import sys
        import termios
        try:
            # Try to restore terminal to sane state
            import subprocess
            subprocess.run(['stty', 'sane'], check=False)
        except:
            pass
        logger.info("Program exited")
