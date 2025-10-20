# Classroom Paper Robot Simulator

A web-based simulation of a classroom robot that can pass out papers, collect tests, and respond to student hand raises.

## Features

- **Interactive Grid**: 18x12 classroom layout with student desks
- **Robot Movement**: Click to move the robot around the classroom
- **Automation Routines**:
  - Pass out papers to all students
  - Collect and grade tests automatically
  - Return to dock for charging
- **Hand Raise Detection**: Students can raise their hands for help
- **Obstacle Management**: Add/remove obstacles in the classroom
- **Grade Reporting**: View student grades and class averages
- **Real-time Status**: Live updates of robot position and tasks

## How to Use

1. **Open `index.html`** in any web browser
2. **Set Target Mode**: Click anywhere to move the robot
3. **Toggle Obstacles**: Add/remove obstacles by clicking cells
4. **Raise Hand**: Simulate students raising their hands
5. **Inspect Desk**: Click desks to see student information
6. **Use Automation**: Click buttons to run automated routines

## Controls

### Interaction Modes
- **Set Target**: Move robot to clicked location
- **Toggle Obstacles**: Add/remove obstacles
- **Raise Hand**: Simulate student hand raises
- **Inspect Desk**: View student status

### Automation Routines
- **Pass Out Papers**: Deliver papers to all students
- **Collect & Grade**: Collect and grade all tests
- **Return to Dock**: Send robot back to charging station
- **Clear Obstacles**: Remove all obstacles
- **Toggle Hand Scanning**: Enable/disable automatic hand detection

## Classroom Layout

- **Green Dock**: Robot charging station (bottom-left)
- **Brown Desks**: Student workstations with IDs (D01-D20)
- **Blue Robot**: Movable classroom assistant
- **White Floor**: Walkable areas
- **Gray Obstacles**: Blocked areas

## Technical Details

- Built with HTML5, CSS3, and JavaScript
- Responsive design works on desktop and mobile
- No external dependencies required
- Cross-browser compatible

## Getting Started

Simply open `index.html` in your web browser - no installation required!

The robot starts at the dock position (1, 10) and is ready to help manage the classroom.
