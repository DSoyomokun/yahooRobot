# Yahoo Robot Classroom Simulator

A web-based classroom robot simulator built with HTML, CSS, and JavaScript. This simulator demonstrates autonomous robot behavior in a classroom environment for paper distribution, test collection, and student assistance.

## Features

### 🤖 Robot Capabilities
- **Autonomous Navigation**: A* pathfinding algorithm for optimal obstacle avoidance
- **Paper Distribution**: Efficient route through all 20 desks
- **Test Collection**: Automated test gathering and grading
- **Hand Raise Response**: Manual response to student requests
- **Collision Avoidance**: Prevents robot from going through desks
- **Speed Control**: Adjustable simulation speed (1x to 4x)

### 🎯 Classroom Management
- **20 Student Desks**: Arranged in a realistic classroom layout
- **Dock Station**: Robot's home base for charging and task completion
- **Student Interaction**: Click desks to raise hands for assistance
- **Grade Management**: Automatic test grading with detailed reports
- **Status Monitoring**: Real-time robot position and task tracking

### 🎮 Controls
- **Pass Out Papers**: Distributes papers to all desks needing them
- **Collect Papers**: Gathers completed tests from all desks
- **Toggle Hand Scanning**: Responds to raised hands (manual mode)
- **Speed Controls**: Increase/decrease simulation speed
- **Grade Report**: View detailed grading results

## Route Optimization

The robot follows an optimized route for maximum efficiency:

**Paper Distribution & Collection Route:**
```
D16 → D11 → D06 → D01 → D02 → D07 → D12 → D17 → D18 → D13 → 
D08 → D03 → D04 → D09 → D14 → D19 → D20 → D15 → D10 → D05 → Dock
```

## Technical Implementation

### Pathfinding
- **A* Algorithm**: Optimal pathfinding around obstacles
- **Collision Detection**: Prevents robot from entering desk areas
- **Edge Positioning**: Robot stops at desk edges, not inside desks

### Task Management
- **Queue System**: Efficient task queuing and execution
- **State Management**: Tracks robot status, desk states, and student needs
- **Interference Prevention**: Prevents task conflicts during execution

### User Interface
- **Grid-Based Layout**: Visual representation of classroom
- **Real-Time Updates**: Live robot position and status updates
- **Interactive Controls**: Click-to-raise hands, button controls
- **Responsive Design**: Works on desktop and mobile devices

## Getting Started

1. **Open the Simulator**:
   ```bash
   # Serve the files locally
   python3 -m http.server 8000
   # Or use any web server
   ```

2. **Access the Simulator**:
   - Open `http://localhost:8000/sim/index.html` in your browser

3. **Basic Usage**:
   - Click desks to raise hands (turns red)
   - Use control buttons to start robot tasks
   - Monitor robot status in the control panel
   - Adjust speed as needed

## Classroom Scenarios

### Paper Distribution
1. Click "Pass Out Papers"
2. Robot follows optimized route
3. Delivers papers to desks needing them
4. Returns to dock when complete

### Test Collection
1. Click "Collect Papers" 
2. Robot visits all desks with completed tests
3. Automatically grades tests
4. Returns to dock with collected tests

### Student Assistance
1. Click desks to raise hands (red indicators)
2. Click "Toggle Hand Scanning"
3. Robot visits all raised hands
4. Clears red indicators as it assists students

## Configuration

### Desk Layout
- 20 desks arranged in 4 rows of 5 desks each
- Each desk is a 4x4 cell area
- Robot stops at desk edges (not inside desks)

### Robot Specifications
- **Size**: Larger than original for better visibility
- **Speed**: Adjustable from 1x to 4x simulation speed
- **Navigation**: A* pathfinding with collision avoidance
- **Positioning**: Stops at desk front edges for realistic behavior

## Development Notes

### Key Features Implemented
- ✅ Manual hand scanning (no automatic movement)
- ✅ Efficient routing for all tasks
- ✅ Proper collision avoidance
- ✅ Edge positioning at desks
- ✅ Speed control
- ✅ Grade reporting for all 20 desks
- ✅ Task queue management
- ✅ Interference prevention

### Technical Details
- **Language**: HTML5, CSS3, JavaScript (ES6+)
- **Pathfinding**: A* algorithm implementation
- **State Management**: Object-oriented design
- **UI Framework**: Vanilla JavaScript with modern CSS
- **Browser Support**: Modern browsers (Chrome, Firefox, Safari, Edge)

## Future Enhancements

- [ ] Multiple robot support
- [ ] Advanced scheduling algorithms
- [ ] Real-time collaboration features
- [ ] Mobile app integration
- [ ] Analytics and reporting dashboard
- [ ] Custom classroom layouts
- [ ] Voice commands integration

## License

This simulator is part of the Yahoo Robot project. See the main repository for licensing information.

## Contributing

Contributions are welcome! Please refer to the main project repository for contribution guidelines.

---

**Note**: This is a simulation environment for testing and demonstration purposes. For actual robot hardware implementation, see the main Yahoo Robot repository.
