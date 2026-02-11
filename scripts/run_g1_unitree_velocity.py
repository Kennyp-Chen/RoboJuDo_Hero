#!/usr/bin/env python3
"""
Unitree Velocity policy deployment script for G1 robot.

This script deploys the original unitree_rl_mjlab velocity control strategy
in the RoboJuDo framework, using the original ONNX model and parameters.

Usage:
    python run_g1_unitree_velocity.py [--sim|--real]

Examples:
    # Run in simulation
    python run_g1_unitree_velocity.py --sim
    
    # Run on real robot
    python run_g1_unitree_velocity.py --real
"""

import argparse
import logging
import os
import sys
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import robojudo.pipeline
from robojudo.config.config_manager import ConfigManager
from robojudo.pipeline.pipeline_cfgs import RlPipelineCfg
from robojudo.pipeline.rl_pipeline import RlPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("g1_unitree_velocity")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Deploy G1 robot with Unitree Velocity policy from unitree_rl_mjlab"
    )
    parser.add_argument(
        "--sim",
        action="store_true",
        default="--sim",
        help="Run in simulation mode"
    )
    parser.add_argument(
        "--real", 
        action="store_true",
        help="Run on real robot"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--policy_name",
        type=str,
        default="policy_demo.onnx",

    )
    return parser.parse_args()


def print_control_instructions():
    """Print control instructions for Unitree Velocity policy."""
    print("\n" + "="*60)
    print("G1 UNITREE VELOCITY POLICY CONTROLS")
    print("="*60)
    
    print("\n🎮 KEYBOARD CONTROLS (unitree_rl_mjlab style):")
    print("  W/S - Forward/Backward movement")
    print("  A/D - Left/Right movement") 
    print("  Q/E - Turn Left/Right")
    print("  ESC  - Exit")
    
    print("\n🎯 UNITREE VELOCITY FEATURES:")
    print("  - Original unitree_rl_mjlab velocity control")
    print("  - WASD+QE keyboard mapping")
    print("  - Enhanced drift compensation")
    print("  - Full 29 DOF control")
    print("  - Real-time velocity visualization")
    
    print("\n📊 VISUALIZATION:")
    print("  - Green arrows: Final velocity commands")
    print("  - Red arrows: Raw input commands (for comparison)")
    print("  - White arrow: Angular velocity command")
    print("  - Status text: Phase and velocity info")
    
    print("\n⚠️  SAFETY NOTES:")
    print("  - Start in simulation mode first")
    print("  - Ensure robot has clear space")
    print("  - Monitor robot behavior closely")
    print("  - Use emergency stop if needed")
    print("="*60)


def validate_model_files(args):
    """Validate that Unitree Velocity model files exist."""
    model_dir = project_root / "assets" / "models" / "g1" / "unitree_mjlab_velocity"
    
    required_files = [
        # "exported/policy_20000.onnx",
        f"exported/{args.policy_name}",
        "params/deploy.yaml"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = model_dir / file_path
        if not full_path.exists():
            missing_files.append(str(full_path))
    
    if missing_files:
        logger.error("Missing Unitree Velocity model files:")
        for file_path in missing_files:
            logger.error(f"  - {file_path}")
        return False
    
    logger.info("✓ Unitree Velocity model files validated")
    return True


def main():
    args = parse_args()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Validate model files
    if not validate_model_files(args):
        logger.error("Model validation failed")
        sys.exit(1)
    
    # Determine config name
    config_name = "g1_unitree_velocity"
    if args.real:
        config_name = f"{config_name}_real"
    
    logger.info(f"Using configuration: {config_name}")
    
    # try:
    # Load configuration
    config_manager = ConfigManager(config_name=config_name)
    cfg: RlPipelineCfg = config_manager.get_cfg()
    
    # Print control instructions
    print_control_instructions()
    
    # Validate configuration
    if not hasattr(cfg, 'pipeline_type'):
        logger.error("Invalid configuration: missing pipeline_type")
        sys.exit(1)
    
    pipeline_type = cfg.pipeline_type
    logger.info(f"Using pipeline: {pipeline_type}")
    
    # Create pipeline
    pipeline_class: type[RlPipeline] = getattr(robojudo.pipeline, pipeline_type)
    logger.info(f"Pipeline class: {pipeline_class}")
    
    pipeline = pipeline_class(cfg=cfg)
    
    # Prepare pipeline for real robot if needed
    if not cfg.env.is_sim:
        logger.info("Preparing pipeline for real robot deployment...")
        pipeline.prepare()
        logger.info("Pipeline preparation completed")
    
    # Main control loop
    logger.info("Starting Unitree Velocity control loop...")
    logger.info("Press Ctrl+C to stop")
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            time_start = time.time()
            
            # Step the pipeline
            pipeline.step()
            
            time_end = time.time()
            time_diff = time_end - time_start
            
            # Maintain desired frequency
            if not cfg.run_fullspeed:
                time_diff = pipeline.dt - time_diff
                if time_diff > 0:
                    time.sleep(time_diff)
                else:
                    if not cfg.env.is_sim:
                        logger.warning(f"Frame drop: {-time_diff:.4f}s")
                        if time_diff < -0.2:
                            logger.critical("Excessive frame drop, shutting down")
                            pipeline.env.shutdown()
                            time.sleep(10)
                            break
            
            frame_count += 1
            
            # Print status every 1000 frames
            if frame_count % 1000 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed
                logger.info(f"Status: {frame_count} frames, {fps:.1f} FPS")
                
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down...")
    
    # Cleanup
    if not cfg.env.is_sim:
        logger.info("Shutting down robot...")
        pipeline.env.shutdown()
    
    logger.info("Unitree Velocity deployment completed successfully")
        
    # except Exception as e:
    #     logger.error(f"Deployment failed: {e}")
    #     if args.debug:
    #         import traceback
    #         traceback.print_exc()
    #     sys.exit(1)


if __name__ == "__main__":
    main()
