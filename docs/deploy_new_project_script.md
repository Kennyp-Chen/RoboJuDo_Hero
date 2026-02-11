# Deploying New Project Scripts in RoboJuDo

This guide provides comprehensive steps for deploying new project scripts and integrating external features into the RoboJuDo framework, using the G1 velocity-enhanced locomotion integration as a reference example.

## Overview

RoboJuDo is designed to be modular and extensible. This guide covers the complete workflow for integrating new policies, configurations, and deployment scripts into the framework.

## Prerequisites

- RoboJuDo project structure properly set up
- Python environment with required dependencies
- Basic understanding of robotics control systems
- Familiarity with configuration management in RoboJuDo

## Step-by-Step Deployment Process

### 1. Analyze External Implementation

Before integration, thoroughly analyze the external codebase:

```bash
# Example: Analyzing unitree_rl_mjlab velocity control
find /path/to/unitree_rl_mjlab -name "*.cpp" -o -name "*.h"
grep -r "velocity" /path/to/unitree_rl_mjlab/deploy/
```

**Key Analysis Points:**
- Control strategy implementation
- Command mapping and processing
- Safety mechanisms
- Integration interfaces

### 2. Create Policy Implementation

Create new policy files in the appropriate directory:

```bash
# Directory structure
RoboJuDo/
├── robojudo/
│   └── policy/
│       ├── __init__.py
│       ├── base_policy.py
│       ├── unitree_policy.py
│       └── g1_velocity_enhanced_policy.py  # New policy
```

**Policy Implementation Template:**

```python
from robojudo.policy import Policy, policy_registry

@policy_registry.register
class NewPolicy(Policy):
    """New policy implementation with enhanced features."""
    
    def __init__(self, cfg_policy, device):
        super().__init__(cfg_policy=cfg_policy, device=device)
        # Initialize policy-specific parameters
    
    def reset(self):
        # Reset policy state
        pass
    
    def get_observation(self, env_data, ctrl_data):
        # Process observations
        return obs, extras
    
    def post_step_callback(self, commands=None):
        # Post-processing after each step
        pass
```

### 3. Create Configuration Classes

Create configuration files for the new policy:

```bash
# Directory structure
RoboJuDo/
├── robojudo/
│   └── config/
│       └── g1/
│           └── policy/
│               ├── __init__.py
│               ├── g1_unitree_policy_cfg.py
│               └── g1_velocity_enhanced_policy_cfg.py  # New config
```

**Configuration Template:**

```python
from robojudo.policy.policy_cfgs import BasePolicyCfg
from robojudo.tools.tool_cfgs import DoFConfig

class NewPolicyCfg(BasePolicyCfg):
    """Configuration for new policy."""
    
    robot: str = "g1"
    policy_name: str = "policy_name"
    
    # DOF configuration
    obs_dof: DoFConfig = YourDoFConfig()
    action_dof: DoFConfig = obs_dof
    
    # Policy-specific parameters
    custom_param: float = 1.0
    safety_limit: float = 2.0
```

### 4. Register New Configurations

Update the main configuration registry:

```python
# File: robojudo/config/g1/g1_cfg.py

# Add imports
from .policy.g1_velocity_enhanced_policy_cfg import G1VelocityEnhancedPolicyCfg

# Register new configuration
@cfg_registry.register
class g1_new_feature(RlPipelineCfg):
    """New configuration with enhanced features."""
    
    robot: str = "g1"
    env: G1MujocoEnvCfg = G1MujocoEnvCfg()
    
    ctrl: list[YourCtrlCfg] = [
        YourCtrlCfg(),
    ]
    
    policy: NewPolicyCfg = NewPolicyCfg()
```

### 5. Create Deployment Scripts

Create specialized deployment scripts:

```bash
# Directory structure
RoboJuDo/
├── scripts/
│   ├── run_pipeline.py
│   └── run_g1_velocity_enhanced.py  # New deployment script
```

**Deployment Script Template:**

```python
#!/usr/bin/env python3
"""Deployment script for new feature."""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import robojudo.pipeline
from robojudo.config.config_manager import ConfigManager

def main():
    args = parse_args()
    
    # Load configuration
    config_manager = ConfigManager(config_name=args.config)
    cfg = config_manager.get_cfg()
    
    # Create and run pipeline
    pipeline_class = getattr(robojudo.pipeline, cfg.pipeline_type)
    pipeline = pipeline_class(cfg=cfg)
    
    # Main control loop
    while True:
        pipeline.step()

if __name__ == "__main__":
    main()
```

### 6. Update Imports and Registries

Ensure all new components are properly imported:

```python
# File: robojudo/policy/__init__.py
from .g1_velocity_enhanced_policy import G1VelocityEnhancedPolicy

# File: robojudo/config/g1/policy/__init__.py
from .g1_velocity_enhanced_policy_cfg import G1VelocityEnhancedPolicyCfg
```

### 7. Testing and Validation

#### Unit Testing

```python
# tests/test_new_policy.py
import unittest
from robojudo.policy.g1_velocity_enhanced_policy import G1VelocityEnhancedPolicy

class TestNewPolicy(unittest.TestCase):
    def test_policy_initialization(self):
        # Test policy initialization
        pass
    
    def test_observation_processing(self):
        # Test observation processing
        pass
```

#### Integration Testing

```bash
# Test in simulation
python scripts/run_g1_velocity_enhanced.py --config g1_locomimic_velocity_enhanced --sim --debug

# Test configuration loading
python -c "from robojudo.config.config_manager import ConfigManager; ConfigManager('g1_locomimic_velocity_enhanced')"
```

### 8. Documentation

Create comprehensive documentation:

```markdown
# New Feature Documentation

## Overview
Description of the new feature and its capabilities.

## Configuration
List of available configurations and their parameters.

## Usage
Step-by-step usage instructions.

## Troubleshooting
Common issues and solutions.
```

## Best Practices

### 1. Code Organization

- Follow RoboJuDo naming conventions
- Use proper directory structure
- Implement proper error handling
- Add comprehensive logging

### 2. Configuration Management

- Use type hints for configuration parameters
- Provide default values
- Document all configuration options
- Use validation where appropriate

### 3. Safety Considerations

- Implement velocity limits
- Add emergency stop mechanisms
- Include safety checks for real robot deployment
- Provide clear warning messages

### 4. Testing Strategy

- Unit tests for individual components
- Integration tests for complete workflows
- Simulation testing before real deployment
- Performance benchmarking

### 5. Documentation Standards

- Clear API documentation
- Usage examples
- Troubleshooting guides
- Configuration reference

## Common Integration Patterns

### 1. Policy Enhancement

```python
# Extend existing policy
class EnhancedPolicy(BasePolicy):
    def __init__(self, cfg_policy, device):
        super().__init__(cfg_policy=cfg_policy, device=device)
        self.enhanced_features = True
```

### 2. Multi-Pipeline Configuration

```python
# Support multiple pipeline types
class MultiFeatureConfig(RlMultiPolicyPipelineCfg):
    policies: list[PolicyCfg] = [
        BasePolicyCfg(),
        EnhancedPolicyCfg(),
    ]
```

### 3. Controller Integration

```python
# Add new controller support
class EnhancedCtrlCfg(BaseCtrlCfg):
    triggers_extra = {
        "custom_key": "[CUSTOM_ACTION]",
    }
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Check file paths and imports
   - Verify `__init__.py` files
   - Ensure proper registration

2. **Configuration Loading**
   - Validate configuration syntax
   - Check parameter types
   - Verify registry registration

3. **Policy Execution**
   - Check model file paths
   - Verify DOF configurations
   - Validate observation dimensions

4. **Real Robot Deployment**
   - Check network connectivity
   - Verify safety configurations
   - Ensure proper permissions

### Debugging Tools

```bash
# Enable debug logging
python scripts/run_script.py --debug

# Check configuration
python -c "from robojudo.config.config_manager import ConfigManager; print(ConfigManager('config_name').get_cfg())"

# Test policy loading
python -c "from robojudo.policy.policy_registry import get_policy_cls; print(get_policy_cls('PolicyName'))"
```

## Performance Optimization

### 1. Computational Efficiency

- Optimize observation processing
- Use vectorized operations
- Minimize memory allocations

### 2. Real-Time Performance

- Monitor frame rates
- Optimize control loops
- Use threading where appropriate

### 3. Memory Management

- Clean up resources properly
- Avoid memory leaks
- Use efficient data structures

## Conclusion

Following these steps ensures proper integration of new features into the RoboJuDo framework while maintaining code quality, safety, and performance. The modular design of RoboJuDo allows for flexible extensions while preserving the overall architecture integrity.

For specific implementation details, refer to the G1 velocity-enhanced locomotion example provided in this repository.
