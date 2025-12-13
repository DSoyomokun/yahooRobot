# ✅ **📌 MVP v2 — "Classroom Paper Assistant Robot"**

## 🎯 **Core Goal**

A mobile robot that operates in a **single row of desks**:

1.  **Delivers papers** to occupied desks, using person detection.
2.  **Returns to origin** after delivery phase.
3.  **Later collects completed papers** from students who raise their hand, using a camera-based scanning system.
4.  **Avoids obstacles** while navigating to intended desks/locations.

**Key interaction mechanisms:** webcam for person/gesture detection, a physical button for delivery confirmation, distance sensing, IMU for stable navigation.

---

# 🧩 **Required Hardware in MVP**

*   **GoPiGo3 robot + Raspberry Pi**
*   **USB Webcam** ← For person detection (delivery) and hand-raise gesture detection (collection).
*   **GoPiGo Distance Sensor (ToF)** ← Obstacle avoidance.
*   **IMU (Accel + Gyro)** ← Stable driving, turns, bump detection.
*   **Tactile Button** ← At robot for delivery confirmation, or potentially at desks if easier for polling feedback.
*   **Paper tray** (static)
*   **Collection box** (static)

---

# 🚦 **System Flow (Phase 1: Delivery)**

## 1️⃣ **Teacher starts the robot**

*   Press a start button or run the program.

## 2️⃣ **Robot follows a preset path along the row of desks**

*   The path is defined (e.g., a 1D array representing desks in a row).
*   **IMU** = keep straight + accurate turns.
*   **ToF** = avoid bumping into chairs/backpacks (with ability to re-plan around obstacles).

## 3️⃣ **At each desk location along the row**

*   Robot stops and uses the **USB Webcam** to detect if a person is present at the desk.
    *   **If person detected:**
        *   Robot delivers a paper (mechanism to be confirmed, e.g., drops into a slot).
        *   Robot waits for student to press a **robot-mounted tactile button** to confirm paper pickup.
    *   **If no person detected:**
        *   Robot skips the desk.

## 4️⃣ **Robot moves to next desk in the row**

## 5️⃣ **Robot returns to origin** when all desks in the row have been visited.

---

# 🚦 **System Flow (Phase 2: Collection)**

## 1️⃣ **Robot returns to origin and waits**

*   Teacher presses a button to signal time to collect.

## 2️⃣ **Robot performs "Desk-Centric Polling" for raised hands**

*   The robot systematically turns its body/camera to "look" at each desk location in the row.
*   It uses the **USB Webcam** for **hand-raise gesture detection** while facing each desk.
*   If a raised hand is detected for a specific desk, that desk is added to a collection queue.
    *   *Self-correction:* Only one student should raise a hand at a time for this simple MVP.

## 3️⃣ **Robot drives ONLY to desks in the collection queue**

*   Uses:
    *   **IMU** for correct movement.
    *   **ToF** to avoid collisions and re-plan paths around obstacles.

## 4️⃣ **Robot stops at each "ready" desk**

*   Student inserts paper into robot's collection slot.
*   The robot utilizes its **Pi Camera and the `scanner` module** (`scanner.py`, `detector.py`) to:
    *   Detect the presence of the paper (brightness-based).
    *   Capture an image of the paper.
    *   Log the scan event and image path to its internal database.
*   Robot confirms scan completion (e.g., via LED feedback) and updates its internal collection queue.

## 5️⃣ **Robot returns to origin when collection queue is empty**

---

# 📦 **MVP Responsibilities (Robot)**

### **Sense**

*   Distance to obstacles (**ToF**)
*   Orientation + turns (**IMU**)
*   **USB Webcam**: Person presence, Hand-raise gestures
*   **Pi Camera**: Paper presence (for scanning)
*   Button events (robot-mounted tactile button)

### **Perceive**

*   "Desk is occupied" (from webcam)
*   "Hand raised at desk X" (from webcam)
*   "Paper present for scanning" (from Pi camera)
*   "Paper collected" (from button input)

### **Plan**

*   Move through the row of desks.
*   Stop or skip desks based on person detection.
*   Determine collection order based on hand-raise polling.
*   Re-plan local paths to navigate around obstacles.
*   Decide when to return to origin.

### **Act**

*   Drive forward/backward/turn.
*   Stop at desks.
*   Confirm delivery (e.g., via LED).
*   Initiate scanning process.
*   Return to origin.

### **Feedback**

*   Log events (CSV, scan database).
*   LEDs or print messages for status (delivery, scanning, errors).
*   Teacher sees when robot is ready.

---

# 🛑 **MVP Does *Not* Include**

❌ Object detection (other than persons/hands/papers)
❌ Complex SLAM/mapping (fixed navigation only)
❌ Robotic arms
❌ Multi-row classroom navigation (single row only)
❌ OCR or advanced paper content analysis
