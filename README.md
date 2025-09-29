# Physical Motion Blur

## 1. Overview
This addon provides the ability to intuitively control Blender's motion blur settings based on a physical camera's **shutter angle** (degrees) or **shutter speed** (seconds). This makes it easy to achieve more realistic and intentional motion blur effects, especially for filmmaking and photorealistic still image creation.

---
## 2. UI Guide

* **Panel Location:**
    `Properties > Render > Motion Blur > Camera Shutter Control`

* **Prerequisite:**
    To use this addon, you must first enable Blender's standard **Motion Blur** setting.

* **Settings Description:**
    
    * **Mode:** Switches the calculation method between `Angle` and `Speed`.
    * **Shutter Angle (°):** Used in **Angle** mode. Sets the shutter opening angle (e.g., `180°`).
    * **Shutter Speed (s):** Used in **Speed** mode. Sets the shutter speed (e.g., `1/50`).
    * **Frame Rate:** Displays and sets the scene's frames per second (FPS).

---
## 3. Behavior of Each Mode

### Angle Mode
This mode sets the shutter open time as a **ratio (%) of a single frame's duration** (e.g., 180° = 50%). The final strength of the blur is determined by the distance an object moves between frames.

* For a **standard animation** (where keyframes are set on specific frames), changing the **FPS** will **not** change the visual appearance of the motion blur, as the distance moved per frame remains the same.
* However, if you adjust your keyframes to maintain a constant ***real-world speed***, a higher **FPS** will result in less movement per frame, causing the motion blur to become **weaker** (shorter).

### Speed Mode
This mode sets the shutter open time as an **absolute time in seconds** (e.g., `1/50` second). The final strength of the blur is determined by the distance an object moves within that specified duration.

* For a **standard animation**, increasing the **FPS** makes the object's physical speed faster, resulting in a **stronger** (longer) motion blur for the same shutter speed.
* However, if you adjust your keyframes to maintain a constant ***real-world speed***, the length of the motion blur will **remain exactly the same** regardless of the **FPS**, because both the exposure time and the object's speed are constant.
