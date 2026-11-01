**[1] set_gripper** `{"opening": 1.0}` → `{"completed": true, "sim_time_s": 0.8}` tip=[0.194, -0.0011, 0.0895] _(grader stage 0)_

**[2] move_to** `{"x": 0.2468999818484391, "y": -0.09070003012678672, "z": 0.07, "pitch_deg": -90, "roll_deg": -30.670430773352898, "speed": 0.5}` → `{"completed": true, "sim_time_s": 2.92}` tip=[0.2467, -0.0906, 0.0698] _(grader stage 0)_

**[3] move_to** `{"x": 0.2468999818484391, "y": -0.09070003012678672, "z": 0.016957398276028338, "pitch_deg": -90, "roll_deg": -30.670430773352898, "speed": 0.2}` → `{"completed": true, "sim_time_s": 4.36}` tip=[0.2517, -0.0923, 0.0275] _(grader stage 1)_

**[4] set_gripper** `{"opening": 0.0}` → `{"completed": true, "sim_time_s": 5.16}` tip=[0.2512, -0.0927, 0.0258] _(grader stage 1)_

**[5] move_to** `{"x": 0.2468999818484391, "y": -0.09070003012678672, "z": 0.09, "pitch_deg": -90, "roll_deg": -30.670430773352898, "speed": 0.3}` → `{"rejected": true, "reason": "unreachable with pitch -90 deg (best IK error 4.2 mm / 2.0 deg). This position IS reachable with pitch_deg in [-80, -70, -60, -50, -40, -30, -20, -10].", "sim_time_s": 5.16}` tip=[0.2512, -0.0927, 0.0258] _(grader stage 1)_

**[6] move_to** `{"x": 0.2468999818484391, "y": -0.09070003012678672, "z": 0.09, "pitch_deg": -80, "roll_deg": -30.670430773352898, "speed": 0.3}` → `{"completed": true, "sim_time_s": 6.12}` tip=[0.2468, -0.0907, 0.0898] _(grader stage 2)_

**[7] move_to** `{"x": 0.2468, "y": 0.1396, "z": 0.09, "pitch_deg": -90, "roll_deg": -30.670430773352898, "speed": 0.3}` → `{"rejected": true, "reason": "unreachable with pitch -90 deg (best IK error 13.7 mm / 7.5 deg). This position IS reachable with pitch_deg in [-80, -70, -60, -50, -40, -30, -20, -10, 0].", "sim_time_s": 6.12}` tip=[0.2468, -0.0907, 0.0898] _(grader stage 2)_

**[8] move_to** `{"x": 0.2468, "y": 0.1396, "z": 0.09, "pitch_deg": -80, "roll_deg": -30.670430773352898, "speed": 0.3}` → `{"completed": true, "sim_time_s": 8.58}` tip=[0.2467, 0.1395, 0.0898] _(grader stage 3)_

**[9] move_to** `{"x": 0.2468, "y": 0.1396, "z": 0.06, "pitch_deg": -90, "roll_deg": -30.670430773352898, "speed": 0.2}` → `{"completed": true, "sim_time_s": 9.68}` tip=[0.2466, 0.1395, 0.0597] _(grader stage 3)_

**[10] set_gripper** `{"opening": 1.0}` → `{"completed": true, "sim_time_s": 10.48}` tip=[0.2466, 0.1395, 0.0597] _(grader stage 4)_

**[11] move_relative** `{"dz": 0.04}` → `{"rejected": true, "reason": "unreachable with pitch -90 deg (best IK error 19.9 mm / 11.2 deg). This position IS reachable with pitch_deg in [-80, -70, -60, -50, -40, -30, -20, -10, 0].", "sim_time_s": 10.48}` tip=[0.2466, 0.1395, 0.0597] _(grader stage 4)_

**[12] finish** `{"success": true, "summary": "oracle script done"}` → `{"ok": true, "sim_time_s": 10.48}` _(grader stage 4)_

