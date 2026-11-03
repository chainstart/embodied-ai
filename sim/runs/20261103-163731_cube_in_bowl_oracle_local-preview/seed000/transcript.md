**[1] set_gripper** `{"opening": 1.0}` → `{"completed": true, "sim_time_s": 0.8}` tip=[0.194, -0.0011, 0.0895] _(grader stage 0)_

**[2] move_to** `{"x": 0.13789998477757714, "y": -0.1323999683108097, "z": 0.07, "pitch_deg": -90, "roll_deg": 111.53748351896763, "speed": 0.5}` → `{"completed": true, "sim_time_s": 3.64}` tip=[0.1378, -0.1323, 0.0699] _(grader stage 0)_

**[3] move_to** `{"x": 0.13789998477757714, "y": -0.1323999683108097, "z": 0.01695739827603223, "pitch_deg": -90, "roll_deg": 111.53748351896763, "speed": 0.2}` → `{"completed": true, "sim_time_s": 5.2}` tip=[0.14, -0.1362, 0.0223] _(grader stage 1)_

**[4] set_gripper** `{"opening": 0.0}` → `{"completed": true, "sim_time_s": 6.0}` tip=[0.1393, -0.1345, 0.0202] _(grader stage 1)_

**[5] move_to** `{"x": 0.13789998477757714, "y": -0.1323999683108097, "z": 0.09, "pitch_deg": -90, "roll_deg": 111.53748351896763, "speed": 0.3}` → `{"completed": true, "sim_time_s": 7.46}` tip=[0.1378, -0.1323, 0.0898] _(grader stage 2)_

**[6] move_to** `{"x": 0.25, "y": -0.1, "z": 0.09, "pitch_deg": -90, "roll_deg": 111.53748351896763, "speed": 0.3}` → `{"rejected": true, "reason": "unreachable with pitch -90 deg (best IK error 14.0 mm / 7.5 deg). This position IS reachable with pitch_deg in [-80, -70, -60, -50, -40, -30, -20, -10, 0].", "sim_time_s": 7.46}` tip=[0.1378, -0.1323, 0.0898] _(grader stage 2)_

**[7] move_to** `{"x": 0.25, "y": -0.1, "z": 0.09, "pitch_deg": -80, "roll_deg": 111.53748351896763, "speed": 0.3}` → `{"completed": true, "sim_time_s": 8.84}` tip=[0.25, -0.0999, 0.0898] _(grader stage 3)_

**[8] move_to** `{"x": 0.25, "y": -0.1, "z": 0.06, "pitch_deg": -90, "roll_deg": 111.53748351896763, "speed": 0.2}` → `{"completed": true, "sim_time_s": 9.92}` tip=[0.2498, -0.0999, 0.0598] _(grader stage 3)_

**[9] set_gripper** `{"opening": 1.0}` → `{"completed": true, "sim_time_s": 10.72}` tip=[0.2498, -0.0999, 0.0598] _(grader stage 4)_

**[10] move_relative** `{"dz": 0.04}` → `{"rejected": true, "reason": "unreachable with pitch -90 deg (best IK error 20.7 mm / 11.5 deg). This position IS reachable with pitch_deg in [-80, -70, -60, -50, -40, -30, -20, -10, 0].", "sim_time_s": 10.72}` tip=[0.2498, -0.0999, 0.0598] _(grader stage 4)_

**[11] finish** `{"success": true, "summary": "oracle script done"}` → `{"ok": true, "sim_time_s": 10.72}` _(grader stage 4)_
