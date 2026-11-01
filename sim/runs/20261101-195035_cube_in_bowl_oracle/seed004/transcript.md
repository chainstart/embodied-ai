**[1] set_gripper** `{"opening": 1.0}` → `{"completed": true, "sim_time_s": 0.8}` tip=[0.194, -0.0011, 0.0895] _(grader stage 0)_

**[2] move_to** `{"x": 0.23770000303515348, "y": -0.2068000234363554, "z": 0.07, "pitch_deg": -90, "roll_deg": 97.37969640128499, "speed": 0.5}` → `{"rejected": true, "reason": "unreachable with pitch -90 deg (best IK error 8.4 mm / 13.9 deg). This position IS reachable with pitch_deg in [-80, -70, -60, -50, -40, -30, -20, -10, 0].", "sim_time_s": 0.8}` tip=[0.194, -0.0011, 0.0895] _(grader stage 0)_

**[3] move_to** `{"x": 0.23770000303515348, "y": -0.2068000234363554, "z": 0.07, "pitch_deg": -80, "roll_deg": 97.37969640128499, "speed": 0.5}` → `{"completed": true, "sim_time_s": 3.84}` tip=[0.239, -0.2083, 0.07] _(grader stage 0)_

**[4] move_to** `{"x": 0.23770000303515348, "y": -0.2068000234363554, "z": 0.016957398276044366, "pitch_deg": -90, "roll_deg": 97.37969640128499, "speed": 0.2}` → `{"completed": true, "sim_time_s": 5.12}` tip=[0.2395, -0.2098, 0.0276] _(grader stage 1)_

**[5] set_gripper** `{"opening": 0.0}` → `{"completed": true, "sim_time_s": 5.92}` tip=[0.2398, -0.2086, 0.0259] _(grader stage 1)_

**[6] move_to** `{"x": 0.23770000303515348, "y": -0.2068000234363554, "z": 0.09, "pitch_deg": -90, "roll_deg": 97.37969640128499, "speed": 0.3}` → `{"rejected": true, "reason": "unreachable with pitch -90 deg (best IK error 11.2 mm / 18.5 deg). This position IS reachable with pitch_deg in [-70, -60, -50, -40, -30, -20, -10, 0, 10].", "sim_time_s": 5.92}` tip=[0.2398, -0.2086, 0.0259] _(grader stage 1)_

**[7] move_to** `{"x": 0.23770000303515348, "y": -0.2068000234363554, "z": 0.09, "pitch_deg": -80, "roll_deg": 97.37969640128499, "speed": 0.3}` → `{"rejected": true, "reason": "unreachable with pitch -80 deg (best IK error 6.7 mm / 7.1 deg). This position IS reachable with pitch_deg in [-70, -60, -50, -40, -30, -20, -10, 0, 10].", "sim_time_s": 5.92}` tip=[0.2398, -0.2086, 0.0259] _(grader stage 1)_

**[8] move_to** `{"x": 0.23770000303515348, "y": -0.2068000234363554, "z": 0.09, "pitch_deg": -70, "roll_deg": 97.37969640128499, "speed": 0.3}` → `{"completed": true, "sim_time_s": 7.66}` tip=[0.2377, -0.2067, 0.0897] _(grader stage 2)_

**[9] move_to** `{"x": 0.303, "y": 0.0057, "z": 0.09, "pitch_deg": -90, "roll_deg": 97.37969640128499, "speed": 0.3}` → `{"rejected": true, "reason": "unreachable with pitch -90 deg (best IK error 20.0 mm / 15.0 deg). This position IS reachable with pitch_deg in [-80, -70, -60, -50, -40, -30, -20, -10, 0].", "sim_time_s": 7.66}` tip=[0.2377, -0.2067, 0.0897] _(grader stage 2)_

**[10] move_to** `{"x": 0.303, "y": 0.0057, "z": 0.09, "pitch_deg": -80, "roll_deg": 97.37969640128499, "speed": 0.3}` → `{"completed": true, "sim_time_s": 9.74}` tip=[0.3029, 0.0057, 0.0898] _(grader stage 3)_

**[11] move_to** `{"x": 0.303, "y": 0.0057, "z": 0.06, "pitch_deg": -90, "roll_deg": 97.37969640128499, "speed": 0.2}` → `{"rejected": true, "reason": "unreachable with pitch -90 deg (best IK error 8.8 mm / 5.9 deg). This position IS reachable with pitch_deg in [-80, -70, -60, -50, -40, -30, -20, -10, 0].", "sim_time_s": 9.74}` tip=[0.3029, 0.0057, 0.0898] _(grader stage 3)_

**[12] move_to** `{"x": 0.303, "y": 0.0057, "z": 0.06, "pitch_deg": -80, "roll_deg": 97.37969640128499, "speed": 0.2}` → `{"completed": true, "sim_time_s": 11.08}` tip=[0.3029, 0.0057, 0.0598] _(grader stage 3)_

**[13] set_gripper** `{"opening": 1.0}` → `{"completed": true, "sim_time_s": 11.88}` tip=[0.3029, 0.0057, 0.0598] _(grader stage 4)_

**[14] move_relative** `{"dz": 0.04}` → `{"rejected": true, "reason": "unreachable with pitch -80 deg (best IK error 5.6 mm / 3.4 deg). This position IS reachable with pitch_deg in [-70, -60, -50, -40, -30, -20, -10, 0, 10].", "sim_time_s": 11.88}` tip=[0.3029, 0.0057, 0.0598] _(grader stage 4)_

**[15] finish** `{"success": true, "summary": "oracle script done"}` → `{"ok": true, "sim_time_s": 11.88}` _(grader stage 4)_

