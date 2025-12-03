# 🚗 GoPiGo Robot Development Workflow (FULL GUIDE)

This document explains **how to connect to the robot**, run code from our repository **without Jupyter**, and sync changes from our laptops to the robot **even though GoPiGo OS is offline**.

---

## 📡 1. Connect to the GoPiGo Robot WiFi

1. Turn the robot **ON**.
2. On your laptop, connect to the robot Wi-Fi:

SSID: GoPiGo
Password: robots1234

3. Your laptop will disconnect from the internet.  
➡️ This is normal.  
GoPiGo OS creates its own **offline local network**.

---

## 🔑 2. SSH into the Raspberry Pi

Open Terminal on your laptop:

**💡 Quick Commands:**

```bash
# Normal SSH (no GUI)
robopi

# SSH with X11 forwarding (for GUI apps like cv2.imshow)
robopi_x
```

**Manual methods:**

```bash
# Normal SSH
ssh pi@10.10.10.10

# SSH with X11 forwarding
ssh -Y pi@10.10.10.10
```

Credentials:

username: pi
password: robots1234

If successful, you'll see something like:

pi@GoPiGo:~ $

You are now inside the robot via SSH.

**📺 GUI Applications (cv2.imshow, etc.):**

If you need to see windows (like camera feeds), use `robopi_x` instead of `robopi`:

1. **Make sure XQuartz is running on your Mac** (open it from Spotlight)
2. Use `robopi_x` to SSH with X11 forwarding
3. Verify X11 is working: `echo $DISPLAY` (should show something like `localhost:10.0`)
4. Run your GUI app - windows will appear on your Mac via XQuartz

**Example:**
```bash
robopi_x                    # SSH with X11
echo $DISPLAY              # Verify forwarding (should show localhost:10.0)
python3 main.py test pi_camera  # Run camera test with GUI
```

⸻

📂 3. Navigate to Our Code Repository on the Robot

Our project folder is stored on the Pi at:

~/yahooRobot

Move into the repo:

cd ~/yahooRobot

Check contents:

ls

You should see folders such as yahoo/, tests/, robot_scanner/, etc.

⸻

🚫 4. We DO NOT Use Jupyter for Development

Do not use:
	•	The GoPiGo dashboard UI
	•	The notebook environment
	•	GUI block-based programming

We are writing real robotic software, not tutorials.

Workflow = SSH + Python + Our Repo

⸻

▶️ 5. Running Code From Our Repository (Directly)

All scripts run like normal Python programs.

Example test command:

python3 tests/test_drive_gopigo.py

Example gesture/camera test:

python3 tests/test_gesture_pi.py

Main robot controller:

python3 main.py

Always run from inside ~/yahooRobot.

⸻

🔁 6. Development Loop (Laptop → Robot)

Step A — Work Normally on Your Mac (with internet)

Your local repo:

/Users/DSoyomokun/yahooRobot

You edit, commit, document, push:

git add .
git commit -m "Add new navigation code"
git push

This is your main source of truth.

**💡 Quick Command:** Use the `gitup` alias to pull latest from GitHub:

```bash
gitup
```

This automatically: commits local changes, pulls remote updates, and pushes back.

⸻

Step B — Sync Code to the Robot (GoPiGo WiFi, offline mode)

Since GoPiGo OS is offline, the Pi cannot git pull.

Instead, we sync laptop → Pi.

**🚀 Quick Command:** Use the `deploypi` alias:

```bash
deploypi
```

This syncs your local repo to the robot with helpful status messages.

**Manual method (if needed):**

rsync -av --delete ~/yahooRobot/ pi@10.10.10.10:~/yahooRobot/

	•	-a preserves files/permissions
	•	-v verbose output
	•	--delete makes Pi copy match your laptop exactly

Backup method (slower, but simple):

scp -r ~/yahooRobot pi@10.10.10.10:~/


⸻

🔄 7. Full Real-World Robotics Workflow

Repeat:
	1.	Write / test code locally (with YouTube, docs, GPT, etc.)
	2.	On normal WiFi: `gitup` (pull latest from GitHub)
	3.	Connect laptop to GoPiGo WiFi
	4.	`deploypi` (sync repo → Pi)
	5.	`robopi` (SSH into robot)
	6.	Run your scripts: `python3 main.py test mac` or `python3 main.py run`
	7.	Observe robot behavior
	8.	Iterate

This is exactly how robotics labs + drone teams do work.

**💡 Pro Tip:** Keep `gitup` and `deploypi` separate because:
	•	`gitup` needs internet (use on normal WiFi)
	•	`deploypi` works offline (use on GoPiGo WiFi)
	•	You might want to pull updates without deploying
	•	You might want to deploy without pulling

⸻

🧠 8. Why This Matters
	•	The Pi is not your dev environment.
	•	It is a robotic endpoint.
	•	Your laptop is where real development happens.

The robot only:
	•	Executes
	•	Reads sensors
	•	Controls hardware
	•	Logs feedback

⸻

🔨 9. Useful Commands Cheat Sheet

**🚀 Quick Aliases (Recommended)**

```bash
gitup          # Pull latest from GitHub (use on normal WiFi)
deploypi       # Sync code to robot (use on GoPiGo WiFi)
robopi         # SSH into robot (normal, no GUI)
robopi_x       # SSH into robot with X11 forwarding (for GUI apps)
fullsync       # Do both gitup + deploypi (ONLY when online)
```

**Manual Commands**

SSH into robot

ssh pi@10.10.10.10

Repo location on robot

cd ~/yahooRobot

Run main program

python3 main.py

Test motors

python3 tests/test_drive_gopigo.py

Test gesture/camera

python3 tests/test_gesture_pi.py

Sync code from laptop → robot

rsync -av --delete ~/yahooRobot/ pi@10.10.10.10:~/yahooRobot/


⸻

🚨 10. Common Problems & Fixes

SSH won’t connect
	•	Make sure you are on GoPiGo WiFi, not school WiFi
	•	Robot must be on
	•	Retry SSH

Robot doesn’t move
	•	Test with test_drive_gopigo.py
	•	Reboot robot
	•	Make sure scripts import easygopigo3

Camera doesn’t open
	•	Wrong capture index
	•	Try:

cv2.VideoCapture(0)
cv2.VideoCapture(1)


⸻

🧱 11. Team Strategy
	•	Laptop = development + GitHub + documentation
	•	Robot = execution platform
	•	Repo = brain of the robot
	•	Use tests in /tests
	•	Keep features modular:
	•	/yahoo/nav
	•	/yahoo/sense
	•	/yahoo/mission
	•	etc.

Do NOT code directly on the Pi, or changes will be lost during sync.

⸻

🎯 12. Our Philosophy

We are not doing a classroom “assignment.”

We are shipping an MVP robot.

Real robotics =

Develop → Sync → Test → Iterate

If you respect that cycle, the robot will get more capable every week.

⸻
