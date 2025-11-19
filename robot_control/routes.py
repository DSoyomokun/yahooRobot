from robot_control.movement import drive_inches, drive_forward, drive_backward
from robot_control.config import *

def pass_one():
    print("P1 HANDOUT START")

    # AISLE 1
    for r in [1,2,3,4]:
        drive_forward(ROW_SPACING)
        stop()
        wait(PAUSE_TIME)

    for r in [4,3,2,1]:
        drive_backward(ROW_SPACING)
        stop()
        wait(PAUSE_TIME)

    shift_right_inches(SHIFT_RIGHT)

    # AISLE 2
    for r in [1,2,3,4]:
        drive_forward(ROW_SPACING)
        stop()
        wait(PAUSE_TIME)

    for r in [4,3,2,1]:
        drive_backward(ROW_SPACING)
        stop()
        wait(PAUSE_TIME)

    shift_right_inches(SHIFT_RIGHT)

    # AISLE 3
    for r in [1,2,3,4]:
        drive_forward(ROW_SPACING)
        stop()
        wait(PAUSE_TIME)

    for r in [4,3,2,1]:
        drive_backward(ROW_SPACING)
        stop()
        wait(PAUSE_TIME)

    go_to_dock()

def pass_two():
    print("P2 PICKUP START")

    aisles = ["A12","A23","A34","A45","A56"]

    for index, aisle in enumerate(aisles):

        if index % 2 == 0:
            row_order = [1,2,3,4]
        else:
            row_order = [4,3,2,1]

        for r in row_order:
            drive_forward(ROW_SPACING)
            stop()
            wait(PAUSE_TIME)

        for r in reversed(row_order):
            drive_backward(ROW_SPACING)
            stop()
            wait(PAUSE_TIME)

        if aisle != "A56":
            shift_right_inches(SHIFT_RIGHT)

    go_to_dock()


