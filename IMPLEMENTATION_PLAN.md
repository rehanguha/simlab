# Physics Implementation Plan

## Overview
This document outlines the implementation plan to add missing physics features to complete the SimLab physics engine.

## Current State
- **Implemented:** ~30% of designed physics
- **Missing:** ~70% of advanced features
- **Status:** Basic physics working, advanced features not implemented

## Implementation Priority

### Phase 1: Core Numerical Methods (High Priority)
1. **Adaptive Timestep Control**
   - Implement RK45 Dormand-Prince method
   - Add error control with rtol/atol
   - Variable timestep limits (min_dt/max_dt)
   - Replace fixed Euler integration

2. **Buoyancy Force**
   - Calculate upward force: F_buoyancy = ρ_air * V * g
   - Apply to vertical acceleration
   - Toggle with buoyancy config parameter

3. **Virtual Mass Effect**
   - Calculate added mass: m_added = 0.5 * ρ_air * V
   - Effective mass: m_eff = m + m_added
   - Apply to all acceleration calculations

### Phase 2: Advanced Aerodynamics (High Priority)
4. **Multi-Regime Drag Coefficient**
   - Implement full Reynolds number correlation
   - Stokes flow (Re ≤ 1): C_d = 24/Re
   - Schiller-Naumann (1 < Re ≤ 1000)
   - Newton regime (1000 < Re ≤ 3×10⁵)
   - Drag crisis and post-crisis regimes
   - Compressibility corrections for Mach > 0.3

5. **Wind Effects**
   - Implement wind velocity calculation
   - Power law wind profile
   - Gust modeling with Ornstein-Uhlenbeck process
   - Relative velocity for drag calculations

### Phase 3: Contact Physics (Medium Priority)
6. **Hertzian Contact Model**
   - Replace simple elastic collision
   - Implement contact force calculation
   - Velocity-dependent coefficient of restitution
   - Surface normal calculation for slopes

7. **Friction Modeling**
   - Static and kinetic friction coefficients
   - Coulomb friction model
   - Tangential impulse calculation
   - Rolling resistance implementation

### Phase 4: Advanced Features (Medium/Low Priority)
8. **Spin Dynamics**
   - Aerodynamic torque calculation
   - Contact torque during ground interaction
   - Advanced spin decay model
   - Spin-dependent lift coefficient

9. **Surface Properties**
   - Slope and roughness effects
   - Material properties (elasticity, friction)
   - Wetness and dampness effects
   - Surface geometry (hills, bumps)

## Implementation Strategy

### Step 1: Create Physics Modules
- `src/simlab/physics/numerical.py` - Adaptive integration
- `src/simlab/physics/contact.py` - Ground contact mechanics
- `src/simlab/physics/wind.py` - Atmospheric effects

### Step 2: Update Core Engine
- Modify `src/simlab/core.py` to use new physics modules
- Replace hardcoded physics with configurable implementations
- Add proper parameter passing

### Step 3: Configuration Integration
- Ensure all config parameters are actually used
- Add validation for physics parameters
- Maintain backward compatibility

### Step 4: Testing
- Create comprehensive tests for new features
- Validate against known physics problems
- Performance testing for numerical methods

## Expected Outcomes

### Before Implementation
- Fixed timestep Euler integration
- Basic drag and gravity only
- Simple elastic collision
- No wind or advanced effects

### After Implementation
- Adaptive RK45 integration with error control
- Complete aerodynamic model with multi-regime drag
- Sophisticated contact mechanics with friction
- Full wind and atmospheric modeling
- Advanced spin dynamics

## Performance Considerations
- Adaptive timestep should improve efficiency
- More complex physics will increase computation time
- Need to balance accuracy vs performance
- Consider caching expensive calculations

## Testing Strategy
1. **Unit Tests:** Each physics module independently
2. **Integration Tests:** Full physics engine
3. **Validation Tests:** Against known analytical solutions
4. **Performance Tests:** Benchmarking and optimization

## Timeline
- **Phase 1:** 2-3 days
- **Phase 2:** 3-4 days  
- **Phase 3:** 2-3 days
- **Phase 4:** 2-3 days
- **Testing & Integration:** 2-3 days

**Total Estimated Time:** 11-16 days

## Success Criteria
- All configuration parameters are used
- Physics accuracy matches documentation
- Performance remains acceptable
- Comprehensive test coverage
- Backward compatibility maintained