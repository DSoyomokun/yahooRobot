"""
Classroom paper-handling robot simulator.

Provides a Tkinter grid environment with automation routines for passing out,
collecting, and grading tests. Obstacles can be added dynamically and the robot
responds to hand raises immediately.
"""

from __future__ import annotations

import heapq
import random
import tkinter as tk
from dataclasses import dataclass, field
from enum import Enum, auto
from tkinter import messagebox, ttk
from typing import Dict, Generator, Iterable, List, Optional, Tuple

Coord = Tuple[int, int]


class CellKind(Enum):
    """Semantic meaning of a grid cell."""

    FLOOR = auto()
    DESK = auto()
    OBSTACLE = auto()
    DOCK = auto()


@dataclass
class Desk:
    """Represents a single student desk within the classroom grid."""

    desk_id: str
    coord: Coord
    student_name: str
    docking_coord: Coord
    needs_paper: bool = True
    has_submitted: bool = False
    answers: Optional[List[str]] = None
    grade: Optional[float] = None
    hand_raised: bool = False


class Grid:
    """Logical representation of the classroom floor as a grid."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self._cells: List[List[CellKind]] = [
            [CellKind.FLOOR for _ in range(width)] for _ in range(height)
        ]
        self.desks: Dict[str, Desk] = {}
        self._desk_by_coord: Dict[Coord, Desk] = {}
        self.dock_position: Coord = (0, 0)

    def in_bounds(self, coord: Coord) -> bool:
        x, y = coord
        return 0 <= x < self.width and 0 <= y < self.height

    def get_cell(self, coord: Coord) -> CellKind:
        x, y = coord
        return self._cells[y][x]

    def set_cell(self, coord: Coord, kind: CellKind) -> None:
        if not self.in_bounds(coord):
            raise ValueError(f"Coordinate {coord} outside of grid bounds")
        x, y = coord
        self._cells[y][x] = kind

    def add_desk(self, desk: Desk) -> None:
        if desk.desk_id in self.desks:
            raise ValueError(f"Desk id {desk.desk_id} already exists")
        if not self.in_bounds(desk.coord):
            raise ValueError(f"Desk coordinate {desk.coord} outside of grid bounds")
        if desk.coord in self._desk_by_coord:
            raise ValueError(f"Coordinate {desk.coord} already has a desk assigned")
        self.set_cell(desk.coord, CellKind.DESK)
        self.desks[desk.desk_id] = desk
        self._desk_by_coord[desk.coord] = desk

    def remove_desk(self, desk_id: str) -> None:
        desk = self.desks.pop(desk_id)
        self.set_cell(desk.coord, CellKind.FLOOR)
        self._desk_by_coord.pop(desk.coord, None)

    def desk_at(self, coord: Coord) -> Optional[Desk]:
        return self._desk_by_coord.get(coord)

    def neighbors(self, coord: Coord) -> Generator[Coord, None, None]:
        x, y = coord
        deltas = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dx, dy in deltas:
            nxt = (x + dx, y + dy)
            if not self.in_bounds(nxt):
                continue
            if self.get_cell(nxt) == CellKind.OBSTACLE:
                continue
            yield nxt

    def iter_cells(self) -> Iterable[Tuple[Coord, CellKind]]:
        for y in range(self.height):
            for x in range(self.width):
                yield (x, y), self._cells[y][x]


class TaskKind(Enum):
    """Classifies the type of work the robot is attempting to complete."""

    PASS_OUT = auto()
    COLLECT = auto()
    HAND_RAISE = auto()
    DOCK = auto()
    IDLE = auto()


@dataclass
class Task:
    """Represents an atomic robotic task with an optional target desk."""

    kind: TaskKind
    target: Optional[Coord] = None
    desk_id: Optional[str] = None


@dataclass
class RobotState:
    """Tracks the operational status of the classroom robot."""

    position: Coord
    carrying_papers: int = 0
    collected_tests: Dict[str, Desk] = field(default_factory=dict)
    task_queue: List[Task] = field(default_factory=list)
    current_task: Optional[Task] = None
    scanning_enabled: bool = True

    def enqueue(self, task: Task) -> None:
        self.task_queue.append(task)

    def dequeue(self) -> Optional[Task]:
        if self.task_queue:
            return self.task_queue.pop(0)
        return None

    def clear_tasks(self) -> None:
        self.task_queue.clear()
        self.current_task = None


# --- Path planning utilities -------------------------------------------------

CELL_SIZE = 48
GRID_OUTLINE = "#b5b5b5"
CELL_COLORS = {
    CellKind.FLOOR: "#f8f8f8",
    CellKind.DESK: "#d9c690",
    CellKind.OBSTACLE: "#6b4f4f",
    CellKind.DOCK: "#7bd58c",
}
ROBOT_COLOR = "#3a88f5"
ROBOT_PATH_COLOR = "#4cce9a"

ANSWER_KEY = ["B", "D", "A", "C", "B", "A", "D", "C", "B", "A"]
MULTIPLE_CHOICE_OPTIONS = ["A", "B", "C", "D"]


def generate_student_answers(seed: int) -> List[str]:
    rng = random.Random(seed * 97)
    return [rng.choice(MULTIPLE_CHOICE_OPTIONS) for _ in ANSWER_KEY]


def manhattan(a: Coord, b: Coord) -> int:
    ax, ay = a
    bx, by = b
    return abs(ax - bx) + abs(ay - by)


def movement_cost(grid: Grid, coord: Coord) -> int:
    kind = grid.get_cell(coord)
    if kind == CellKind.DESK:
        return 2
    return 1


def reconstruct_path(came_from: Dict[Coord, Coord], start: Coord, goal: Coord) -> List[Coord]:
    current = goal
    path = [current]
    while current != start:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path


def a_star(grid: Grid, start: Coord, goal: Coord) -> List[Coord]:
    if not grid.in_bounds(goal):
        return []
    if grid.get_cell(goal) == CellKind.OBSTACLE:
        return []

    frontier: List[Tuple[int, Coord]] = []
    heapq.heappush(frontier, (0, start))
    came_from: Dict[Coord, Coord] = {}
    cost_so_far: Dict[Coord, int] = {start: 0}

    while frontier:
        _, current = heapq.heappop(frontier)
        if current == goal:
            return reconstruct_path(came_from, start, goal)

        for nxt in grid.neighbors(current):
            cell_kind = grid.get_cell(nxt)
            if cell_kind == CellKind.DESK and nxt != goal:
                continue
            new_cost = cost_so_far[current] + movement_cost(grid, nxt)
            if new_cost < cost_so_far.get(nxt, float("inf")):
                cost_so_far[nxt] = new_cost
                priority = new_cost + manhattan(nxt, goal)
                heapq.heappush(frontier, (priority, nxt))
                came_from[nxt] = current

    return []


# --- Classroom scaffolding ---------------------------------------------------


def build_default_classroom() -> Tuple[Grid, RobotState]:
    """Produce a baseline classroom layout inspired by the reference photos."""

    grid = Grid(width=18, height=12)

    grid.dock_position = (1, grid.height - 2)
    grid.set_cell(grid.dock_position, CellKind.DOCK)

    student_names = [
        "Alex",
        "Brooke",
        "Chris",
        "Devon",
        "Emery",
        "Frankie",
        "Genesis",
        "Harper",
        "Indy",
        "Jordan",
        "Kai",
        "Logan",
        "Morgan",
        "Nico",
        "Oakley",
        "Parker",
    ]

    desk_positions = [
        (3, [5, 7, 9, 11, 13]),
        (5, [5, 7, 9, 11, 13]),
        (7, [5, 7, 9, 11, 13]),
        (9, [5, 7, 9, 11, 13]),
    ]

    desk_id = 1
    for row_y, xs in desk_positions:
        for x in xs:
            name = student_names[(desk_id - 1) % len(student_names)]
            dock_x = max(0, x - 1)
            docking = (dock_x, row_y)
            desk = Desk(
                desk_id=f"D{desk_id:02d}",
                coord=(x, row_y),
                student_name=name,
                docking_coord=docking,
                answers=generate_student_answers(desk_id),
            )
            grid.add_desk(desk)
            desk_id += 1

    robot = RobotState(position=grid.dock_position)
    robot.carrying_papers = len(grid.desks)
    return grid, robot


# --- Visualization and automation -------------------------------------------


class ClassroomSim:
    """Tkinter-powered visualization and task automation for the classroom robot."""

    def __init__(self, grid: Grid, robot_state: RobotState) -> None:
        self.grid = grid
        self.robot_state = robot_state
        self.root = tk.Tk()
        self.root.title("Classroom Paper Robot Simulator")
        self.mode = tk.StringVar(value="target")
        self.status_var = tk.StringVar(value="Ready for instructions.")
        self.task_var = tk.StringVar(value="Idle")
        self.robot_path: List[Coord] = []
        self.display_path: List[Coord] = []
        self.history: List[str] = []
        self.tick_interval_ms = 220
        self.scan_interval_ms = 1000  # Scan every second
        self._build_ui()
        self.update_task_label()
        self.render()
        self.root.after(self.tick_interval_ms, self.tick)
        self.root.after(self.scan_interval_ms, self.scan_for_hand_raises)

    # -- UI assembly ---------------------------------------------------------

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        main = ttk.Frame(self.root, padding=6)
        main.grid(row=0, column=0, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(0, weight=1)

        canvas_width = self.grid.width * CELL_SIZE
        canvas_height = self.grid.height * CELL_SIZE
        self.canvas = tk.Canvas(
            main,
            width=canvas_width,
            height=canvas_height,
            background="#ffffff",
            highlightthickness=0,
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        controls = ttk.Frame(main, padding=(12, 0))
        controls.grid(row=0, column=1, sticky="ns")

        ttk.Label(controls, text="Interaction Mode", font=("", 10, "bold")).pack(
            anchor="w", pady=(0, 4)
        )
        ttk.Radiobutton(
            controls,
            text="Set Target",
            value="target",
            variable=self.mode,
            command=lambda: self.set_status(
                "Target mode: click a cell to route the robot."
            ),
        ).pack(anchor="w")
        ttk.Radiobutton(
            controls,
            text="Toggle Obstacles",
            value="obstacle",
            variable=self.mode,
            command=lambda: self.set_status(
                "Obstacle mode: click to add/remove an obstacle."
            ),
        ).pack(anchor="w")
        ttk.Radiobutton(
            controls,
            text="Raise Hand",
            value="handraise",
            variable=self.mode,
            command=lambda: self.set_status(
                "Hand raise: click a desk to request pickup."
            ),
        ).pack(anchor="w")
        ttk.Radiobutton(
            controls,
            text="Inspect",
            value="select",
            variable=self.mode,
            command=lambda: self.set_status(
                "Inspect mode: click a desk to view its status."
            ),
        ).pack(anchor="w")

        ttk.Separator(controls, orient="horizontal").pack(fill="x", pady=8)

        ttk.Button(
            controls,
            text="Clear Added Obstacles",
            command=self.clear_obstacles,
        ).pack(fill="x", pady=2)
        
        ttk.Button(
            controls,
            text="Toggle Scanning",
            command=self.toggle_scanning,
        ).pack(fill="x", pady=2)

        ttk.Label(controls, text="Routines", font=("", 10, "bold")).pack(
            anchor="w", pady=(12, 4)
        )
        ttk.Button(
            controls,
            text="Pass Out Papers",
            command=self.start_pass_out,
        ).pack(fill="x", pady=2)
        ttk.Button(
            controls,
            text="Collect & Grade",
            command=self.start_collection,
        ).pack(fill="x", pady=2)
        ttk.Button(
            controls,
            text="Return to Dock",
            command=self.queue_return_to_dock,
        ).pack(fill="x", pady=2)
        ttk.Button(
            controls,
            text="Cancel Routine",
            command=self.cancel_current_routine,
        ).pack(fill="x", pady=2)
        ttk.Button(
            controls,
            text="Show Grade Report",
            command=self.show_grade_report,
        ).pack(fill="x", pady=2)

        ttk.Label(controls, text="Task Status", font=("", 10, "bold")).pack(
            anchor="w", pady=(12, 4)
        )
        ttk.Label(
            controls,
            textvariable=self.task_var,
            wraplength=220,
            padding=(0, 2),
        ).pack(anchor="w", fill="x")

        ttk.Label(controls, text="Latest Update", font=("", 10, "bold")).pack(
            anchor="w", pady=(12, 4)
        )
        ttk.Label(
            controls,
            textvariable=self.status_var,
            wraplength=220,
            padding=(0, 2),
        ).pack(anchor="w", fill="x")

        self.canvas.bind("<Button-1>", self.on_canvas_click)

    # -- Event handlers ------------------------------------------------------

    def on_canvas_click(self, event: tk.Event) -> None:
        coord = self.pixel_to_grid(event.x, event.y)
        if not self.grid.in_bounds(coord):
            return

        mode = self.mode.get()
        if mode == "obstacle":
            self.toggle_obstacle(coord)
        elif mode == "target":
            self.set_robot_target(coord)
        elif mode == "handraise":
            self.raise_hand_at(coord)
        elif mode == "select":
            self.inspect_cell(coord)

    def toggle_obstacle(self, coord: Coord) -> None:
        kind = self.grid.get_cell(coord)
        if kind in (CellKind.DESK, CellKind.DOCK):
            self.set_status("Cannot place an obstacle on a desk or docking station.")
            return
        new_kind = CellKind.OBSTACLE if kind != CellKind.OBSTACLE else CellKind.FLOOR
        self.grid.set_cell(coord, new_kind)
        self.set_status(
            f"Obstacle {'added' if new_kind == CellKind.OBSTACLE else 'removed'} at {coord}."
        )
        self.render()

    def set_robot_target(self, coord: Coord) -> None:
        self.cancel_current_routine(quiet=True)
        start = self.robot_state.position
        path = a_star(self.grid, start, coord)
        if not path:
            self.set_status(f"No path to {coord}; check for blocked aisles.")
            return
        self.robot_path = path[1:]
        self.display_path = path
        self.robot_state.current_task = None
        self.task_var.set(f"Manual route to {coord}")
        self.set_status(f"Manual routing to {coord}.")

    def raise_hand_at(self, coord: Coord) -> None:
        desk = self.grid.desk_at(coord)
        if not desk:
            self.set_status("Hand raise requests must be made on a desk cell.")
            return
        self.set_status(f"{desk.student_name} at {desk.desk_id} raised their hand.")
        task = Task(TaskKind.HAND_RAISE, target=desk.docking_coord, desk_id=desk.desk_id)
        self.interrupt_with_task(task)

    def inspect_cell(self, coord: Coord) -> None:
        desk = self.grid.desk_at(coord)
        if desk:
            status_bits = []
            status_bits.append("Needs paper" if desk.needs_paper else "Has paper")
            status_bits.append("Submitted" if desk.has_submitted else "Pending submission")
            grade = f"{desk.grade:.0f}%" if desk.grade is not None else "Ungraded"
            status_bits.append(grade)
            if desk.hand_raised:
                status_bits.append("Hand raised")
            self.set_status(
                f"{desk.desk_id} ({desk.student_name}): {', '.join(status_bits)}."
            )
        else:
            kind = self.grid.get_cell(coord).name
            self.set_status(f"Cell {coord} is {kind}.")

    def clear_obstacles(self) -> None:
        cleared = 0
        for (cell_coord, kind) in list(self.grid.iter_cells()):
            if kind == CellKind.OBSTACLE:
                self.grid.set_cell(cell_coord, CellKind.FLOOR)
                cleared += 1
        self.set_status(f"Cleared {cleared} obstacle cells.")
        self.render()
    
    def toggle_scanning(self) -> None:
        self.robot_state.scanning_enabled = not self.robot_state.scanning_enabled
        status = "enabled" if self.robot_state.scanning_enabled else "disabled"
        self.set_status(f"Hand raise scanning {status}.")

    def scan_for_hand_raises(self) -> None:
        """Continuously scan for raised hands and respond immediately."""
        if not self.robot_state.scanning_enabled:
            self.root.after(self.scan_interval_ms, self.scan_for_hand_raises)
            return
            
        raised_hands = [desk for desk in self.grid.desks.values() if desk.hand_raised]
        
        if raised_hands:
            # Find the closest raised hand
            closest_desk = min(raised_hands, 
                             key=lambda d: manhattan(self.robot_state.position, d.coord))
            
            # Only interrupt if we're not already handling a hand raise
            current_task = self.robot_state.current_task
            if not current_task or current_task.kind != TaskKind.HAND_RAISE:
                self.set_status(f"Detected raised hand: {closest_desk.student_name} at {closest_desk.desk_id}")
                task = Task(TaskKind.HAND_RAISE, target=closest_desk.coord, desk_id=closest_desk.desk_id)
                self.interrupt_with_task(task)
        
        # Schedule next scan
        self.root.after(self.scan_interval_ms, self.scan_for_hand_raises)

    def interrupt_with_task(self, task: Task) -> None:
        current = self.robot_state.current_task
        if current:
            self.robot_state.task_queue.insert(0, current)
            self.robot_state.current_task = None
        self.robot_state.task_queue.insert(0, task)
        self.cancel_current_motion()
        self.try_start_next_task()
        self.update_task_label()

    # -- Routine controls ----------------------------------------------------

    def start_pass_out(self) -> None:
        desks = [desk for desk in self.desk_visit_order() if desk.needs_paper]
        if not desks:
            self.set_status("All students already have papers.")
            return
        tasks = [
            Task(TaskKind.PASS_OUT, target=desk.docking_coord, desk_id=desk.desk_id)
            for desk in desks
        ]
        self.robot_state.carrying_papers = len(tasks)
        self.schedule_routine(tasks, finish_at_dock=True)
        self.set_status(f"Starting pass-out routine for {len(tasks)} desks.")

    def start_collection(self) -> None:
        desks = [desk for desk in self.desk_visit_order() if not desk.has_submitted]
        if not desks:
            self.set_status("No outstanding tests to collect.")
            return
        tasks = [
            Task(TaskKind.COLLECT, target=desk.docking_coord, desk_id=desk.desk_id)
            for desk in desks
        ]
        self.schedule_routine(tasks, finish_at_dock=True)
        self.set_status(f"Collecting and grading {len(tasks)} tests.")

    def queue_return_to_dock(self) -> None:
        if self.robot_state.current_task and self.robot_state.current_task.kind == TaskKind.DOCK:
            self.set_status("Already returning to the dock.")
            return
        if any(task.kind == TaskKind.DOCK for task in self.robot_state.task_queue):
            self.set_status("Docking request already queued.")
            return
        dock_task = Task(TaskKind.DOCK, target=self.grid.dock_position)
        self.robot_state.enqueue(dock_task)
        self.set_status("Docking request queued.")
        if not self.robot_path and self.robot_state.current_task is None:
            self.try_start_next_task()
        self.update_task_label()

    def cancel_current_routine(self, quiet: bool = False) -> None:
        self.cancel_current_motion()
        self.robot_state.clear_tasks()
        if not quiet:
            self.set_status("Cancelled routine; robot awaiting instructions.")
        self.update_task_label()

    def schedule_routine(self, tasks: List[Task], finish_at_dock: bool = True) -> None:
        self.cancel_current_routine(quiet=True)
        for task in tasks:
            self.robot_state.enqueue(task)
        if finish_at_dock:
            self.robot_state.enqueue(Task(TaskKind.DOCK, target=self.grid.dock_position))
        self.try_start_next_task()
        self.update_task_label()

    def desk_visit_order(self) -> List[Desk]:
        columns: Dict[int, List[Desk]] = {}
        for desk in self.grid.desks.values():
            columns.setdefault(desk.coord[0], []).append(desk)
        ordered: List[Desk] = []
        reverse = False
        for col_x in sorted(columns.keys()):
            desk_column = sorted(columns[col_x], key=lambda d: d.coord[1], reverse=reverse)
            ordered.extend(desk_column)
            reverse = not reverse
        return ordered

    # -- Task execution ------------------------------------------------------

    def try_start_next_task(self) -> None:
        if self.robot_state.current_task or not self.robot_state.task_queue:
            self.update_task_label()
            return

        next_task = self.robot_state.dequeue()
        if next_task is None:
            self.update_task_label()
            return

        target = next_task.target or self.grid.dock_position
        path = a_star(self.grid, self.robot_state.position, target)
        if not path:
            self.set_status(f"Path blocked for {self.describe_task(next_task)}; skipping.")
            self.robot_state.current_task = None
            self.update_task_label()
            self.try_start_next_task()
            return

        self.robot_state.current_task = next_task
        self.robot_path = path[1:]
        self.display_path = path
        self.set_status(f"Heading to {self.describe_task(next_task)}.")
        self.update_task_label()

        if not self.robot_path:
            self.handle_task_arrival()

    def handle_task_arrival(self) -> None:
        task = self.robot_state.current_task
        if not task:
            return

        if task.kind == TaskKind.PASS_OUT:
            self.complete_pass_out(task)
        elif task.kind == TaskKind.COLLECT:
            self.complete_collection(task)
        elif task.kind == TaskKind.HAND_RAISE:
            self.complete_hand_raise(task)
        elif task.kind == TaskKind.DOCK:
            self.set_status("Robot docked and charging.")

        self.robot_state.current_task = None
        self.display_path = []
        self.update_task_label()
        self.try_start_next_task()

    def complete_pass_out(self, task: Task) -> None:
        desk = self.get_task_desk(task)
        if not desk:
            self.set_status("Desk missing during pass-out; skipping.")
            return
        if desk.needs_paper:
            desk.needs_paper = False
            self.robot_state.carrying_papers = max(0, self.robot_state.carrying_papers - 1)
            self.set_status(f"Delivered papers to {desk.desk_id} ({desk.student_name}).")
        else:
            self.set_status(f"{desk.desk_id} already has papers.")

    def complete_collection(self, task: Task) -> None:
        desk = self.get_task_desk(task)
        if not desk:
            self.set_status("Desk missing during collection; skipping.")
            return
        if desk.has_submitted:
            if desk.grade is not None:
                self.set_status(
                    f"Already collected from {desk.desk_id}; recorded {desk.grade:.0f}%."
                )
            else:
                self.set_status(f"{desk.desk_id} already submitted; grading pending.")
            return
        desk.has_submitted = True
        grade = self.scan_and_grade(desk)
        self.set_status(
            f"Collected and scanned {desk.desk_id} ({desk.student_name}) — {grade:.0f}%."
        )

    def complete_hand_raise(self, task: Task) -> None:
        desk = self.get_task_desk(task)
        if not desk:
            self.set_status("Hand raise target missing; skipping.")
            return
        
        # Clear the hand raised flag
        desk.hand_raised = False
        
        if desk.needs_paper:
            desk.needs_paper = False
            self.set_status(f"Delivered replacement paper to {desk.desk_id}.")
        elif not desk.has_submitted:
            self.set_status(f"Checked in with {desk.desk_id}; student resumes work.")
        else:
            self.set_status(f"Collected question from {desk.desk_id}; all set.")

    def get_task_desk(self, task: Task) -> Optional[Desk]:
        if task.desk_id and task.desk_id in self.grid.desks:
            return self.grid.desks[task.desk_id]
        if task.target:
            return self.grid.desk_at(task.target)
        return None

    # -- Reporting -----------------------------------------------------------

    def scan_and_grade(self, desk: Desk) -> float:
        if desk.answers is None:
            desk.answers = generate_student_answers(int(desk.desk_id[1:]))
        correct = sum(
            1 for response, solution in zip(desk.answers, ANSWER_KEY) if response == solution
        )
        grade = round((correct / len(ANSWER_KEY)) * 100, 1)
        desk.grade = grade
        self.robot_state.collected_tests[desk.desk_id] = desk
        return grade

    def show_grade_report(self) -> None:
        graded = [desk for desk in self.grid.desks.values() if desk.grade is not None]
        if not graded:
            messagebox.showinfo(
                "Scanned Test Scores", "No graded tests yet – run a collection routine first."
            )
            return
        graded.sort(key=lambda d: d.desk_id)
        lines = [
            f"{desk.desk_id}: {desk.grade:.0f}% ({desk.student_name})"
            for desk in graded
        ]
        average = sum(desk.grade for desk in graded) / len(graded)
        lines.append("")
        lines.append(f"Class average: {average:.1f}%")
        messagebox.showinfo("Scanned Test Scores", "\n".join(lines))

    # -- Simulation loop -----------------------------------------------------

    def tick(self) -> None:
        if self.robot_path:
            next_coord = self.robot_path.pop(0)
            self.robot_state.position = next_coord
            if not self.robot_path:
                if self.robot_state.current_task:
                    self.handle_task_arrival()
                else:
                    self.set_status(f"Arrived at {next_coord}.")
                    self.display_path = []
                    self.update_task_label()
        else:
            if self.robot_state.current_task is None and self.robot_state.task_queue:
                self.try_start_next_task()

        self.render()
        self.root.after(self.tick_interval_ms, self.tick)

    # -- Rendering -----------------------------------------------------------

    def render(self) -> None:
        self.canvas.delete("all")
        for (x, y), kind in self.grid.iter_cells():
            x0 = x * CELL_SIZE
            y0 = y * CELL_SIZE
            x1 = x0 + CELL_SIZE
            y1 = y0 + CELL_SIZE
            color = CELL_COLORS.get(kind, "#ffffff")
            self.canvas.create_rectangle(
                x0,
                y0,
                x1,
                y1,
                fill=color,
                outline=GRID_OUTLINE,
            )
            desk = self.grid.desk_at((x, y))
            if desk:
                label = desk.desk_id
                if desk.grade is not None:
                    label = f"{desk.desk_id}\n{desk.grade:.0f}%"
                self.canvas.create_text(
                    x0 + CELL_SIZE / 2,
                    y0 + CELL_SIZE / 2,
                    text=label,
                    font=("", 8, "bold"),
                    fill="#333333",
                )
                
                # Draw hand raise indicator
                if desk.hand_raised:
                    # Draw a red circle in the top-right corner
                    indicator_x = x1 - 8
                    indicator_y = y0 + 8
                    self.canvas.create_oval(
                        indicator_x - 6,
                        indicator_y - 6,
                        indicator_x + 6,
                        indicator_y + 6,
                        fill="#ff4444",
                        outline="#cc0000",
                        width=2,
                    )
                    # Add "!" text
                    self.canvas.create_text(
                        indicator_x,
                        indicator_y,
                        text="!",
                        font=("", 10, "bold"),
                        fill="white",
                    )

        if self.display_path:
            self.draw_path(self.display_path, ROBOT_PATH_COLOR)

        self.draw_robot()

    def draw_path(self, path: List[Coord], color: str) -> None:
        if len(path) < 2:
            return
        points: List[int] = []
        for coord in path:
            center = self.grid_to_pixel_center(coord)
            points.extend(center)
        self.canvas.create_line(*points, fill=color, width=3, capstyle=tk.ROUND)

    def draw_robot(self) -> None:
        cx, cy = self.grid_to_pixel_center(self.robot_state.position)
        radius = CELL_SIZE * 0.35
        self.canvas.create_oval(
            cx - radius,
            cy - radius,
            cx + radius,
            cy + radius,
            fill=ROBOT_COLOR,
            outline="#1f4e96",
            width=2,
        )

    # -- Helpers -------------------------------------------------------------

    def pixel_to_grid(self, px: int, py: int) -> Coord:
        return px // CELL_SIZE, py // CELL_SIZE

    def grid_to_pixel_center(self, coord: Coord) -> Tuple[int, int]:
        gx, gy = coord
        return (
            int(gx * CELL_SIZE + CELL_SIZE / 2),
            int(gy * CELL_SIZE + CELL_SIZE / 2),
        )

    def describe_task(self, task: Task) -> str:
        label = {
            TaskKind.PASS_OUT: "Pass-out",
            TaskKind.COLLECT: "Collect",
            TaskKind.HAND_RAISE: "Hand-raise",
            TaskKind.DOCK: "Dock",
            TaskKind.IDLE: "Idle",
        }[task.kind]
        if task.desk_id:
            label += f" → {task.desk_id}"
        elif task.kind == TaskKind.DOCK:
            label += " → Dock"
        elif task.target:
            label += f" → {task.target}"
        return label

    def update_task_label(self) -> None:
        current = self.robot_state.current_task
        queue = self.robot_state.task_queue
        if current:
            desc = self.describe_task(current)
            remaining = len(queue)
            if remaining:
                self.task_var.set(f"{desc} (+{remaining} queued)")
            else:
                self.task_var.set(desc)
        elif queue:
            next_desc = self.describe_task(queue[0])
            extra = len(queue) - 1
            if extra:
                self.task_var.set(f"Next: {next_desc} (+{extra})")
            else:
                self.task_var.set(f"Next: {next_desc}")
        else:
            self.task_var.set("Idle")

    def set_status(self, message: str) -> None:
        self.status_var.set(message)
        self.history.append(message)
        if len(self.history) > 5:
            self.history.pop(0)

    def cancel_current_motion(self) -> None:
        self.robot_path = []
        self.display_path = []
        self.robot_state.current_task = None

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    grid, robot = build_default_classroom()
    sim = ClassroomSim(grid, robot)
    sim.run()


if __name__ == "__main__":
    main()
