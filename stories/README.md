# Yahoo Robot - User Stories

This directory contains all user stories for the MVP development, organized by epic/phase.

## Story Organization

### Epic 1: Foundation & Core Navigation
**Status:** In Progress (Story 1.5 Complete)

Foundational navigation capabilities for the robot to traverse the row of desks.

- `1.1_Configure_Row_of_Desks.md` - Define desk layout configuration
- `1.2_Test_Linear_Movement.md` - Validate straight-line driving
- `1.3_Test_Precise_Turns.md` - Validate turning accuracy
- `1.4_Execute_Full_Row_Traversal.md` - End-to-end row navigation
- `1.5_Implement_Basic_Obstacle_Stop.md` - ✅ **COMPLETE** - Obstacle detection & avoidance

### Epic 2: Perception & Sensing
**Status:** Not Started

Perception systems for person detection, hand-raise detection, button input, and paper scanning.

- `2.1_Simple_Person_Detection.md` - Detect if person present at desk
- `2.2_Desk_Centric_Polling.md` - Scan desks for raised hands
- `2.3_GPIO_Button_Integration.md` - Physical button for delivery confirmation
- `2.4_Paper_Scanning_Integration.md` - Scan collected papers with Pi Camera

### Epic 3: Integration & Missions
**Status:** Not Started

Complete mission workflows that integrate navigation and perception.

- `3.1_Delivery_Mission.md` - Full delivery workflow (navigate + detect + deliver)
- `3.2_Collection_Mission.md` - Full collection workflow (poll + navigate + scan)
- `3.3_Full_MVP_Integration.md` - Complete MVP with both missions + testing

## Development Roadmap

```
Phase 1: Foundation (Epic 1) → 4 weeks
  ├─ Week 1: Stories 1.1, 1.2
  ├─ Week 2: Stories 1.3, 1.4
  └─ Week 3-4: Testing & refinement
  ✅ Story 1.5 already complete

Phase 2: Perception (Epic 2) → 3 weeks
  ├─ Week 5: Stories 2.1, 2.3 (person detection, button)
  └─ Week 6-7: Stories 2.2, 2.4 (polling, scanning)

Phase 3: Integration (Epic 3) → 3 weeks
  ├─ Week 8: Story 3.1 (delivery mission)
  ├─ Week 9: Story 3.2 (collection mission)
  └─ Week 10: Story 3.3 (full integration & testing)

Total: ~10 weeks to MVP
```

## Story Status Legend

- ✅ **COMPLETE** - Implementation done and tested
- 🚧 **IN PROGRESS** - Currently being implemented
- 📋 **READY** - Dependencies met, ready to start
- ⏸️ **BLOCKED** - Waiting on dependencies
- ⏭️ **FUTURE** - Post-MVP enhancement

## Dependencies

```
Story Dependencies:
  1.1 → 1.2 → 1.4
  1.1 → 1.3 → 1.4
  1.4 → All Epic 2 & 3 stories

  2.1 → 3.1
  2.3 → 3.1
  2.2 → 3.2
  2.4 → 3.2

  3.1 + 3.2 → 3.3
```

## Key Concepts & Documentation

- [Desk-Centric Polling Strategy](../docs/DESK_CENTRIC_POLLING.md) - How the robot identifies which desk has a raised hand
- [MVP v2 Overview](../MVP_v2.md) - Overall project goals and requirements
- [Gesture Detection](../docs/GESTURE_DETECTION.md) - Hand-raise detection system
- [Robot Development Workflow](../docs/ROBOT_DEV_WORKFLOW.md) - How to develop and deploy code

## Getting Started

**To start implementing stories:**

1. Read the MVP document: `../MVP_v2.md`
2. Review architecture: `../docs/README.md`
3. Start with Epic 1, Story 1.1
4. Each story is self-contained with:
   - Clear description
   - Detailed tasks
   - Acceptance criteria
   - Test scenarios

**Story Template:**
Each story follows this format:
- **Epic** - Which phase it belongs to
- **Description** - What needs to be built
- **Tasks** - Step-by-step implementation tasks
- **Acceptance Criteria** - How to know it's done
- **Design Considerations** - Important technical notes
- **Integration Points** - What it connects to

## Current Focus

**Next Up: Story 1.1 - Configure Row of Desks**

This is the foundation for all navigation. We need to:
1. Define desk positions in configuration
2. Create simple loader to read config
3. Test that navigation can use the positions

**Why Start Here:**
- All navigation depends on knowing where desks are
- Simple, low-risk starting point
- Can be tested without robot hardware (simulation)
- Provides foundation for Stories 1.2-1.4

## Questions?

See the main [README.md](../README.md) for project setup and development workflow.

For design decisions, check [docs/](../docs/) folder.

---

**Last Updated:** 2025-12-13
**Current Epic:** Epic 1 - Foundation & Core Navigation
**Current Story:** 1.1 - Configure Row of Desks
