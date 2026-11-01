**[1] set_gripper** `{"opening": 1.0}` → `{"completed": true, "sim_time_s": 0.8}` tip=[0.194, -0.0011, 0.0895] _(grader stage 0)_

**[2] move_to** `{"x": 0.31790001457408523, "y": 0.07269985012791978, "z": 0.07, "pitch_deg": -90, "roll_deg": 101.9862770741368, "speed": 0.5}` → `{"rejected": true, "reason": "unreachable with pitch -90 deg (best IK error 7.0 mm / 14.3 deg). This position IS reachable with pitch_deg in [-80, -70, -60, -50, -40, -30, -20, -10, 0].", "sim_time_s": 0.8}` tip=[0.194, -0.0011, 0.0895] _(grader stage 0)_

**[3] move_to** `{"x": 0.31790001457408523, "y": 0.07269985012791978, "z": 0.07, "pitch_deg": -80, "roll_deg": 101.9862770741368, "speed": 0.5}` → `{"completed": true, "sim_time_s": 3.88}` tip=[0.3203, 0.0732, 0.07] _(grader stage 0)_

**[4] move_to** `{"x": 0.31790001457408523, "y": 0.07269985012791978, "z": 0.016957398276005155, "pitch_deg": -90, "roll_deg": 101.9862770741368, "speed": 0.2}` → `{"completed": true, "sim_time_s": 5.1}` tip=[0.3174, 0.0721, 0.0198] _(grader stage 1)_

**[5] set_gripper** `{"opening": 0.0}` → `{"completed": true, "sim_time_s": 5.9}` tip=[0.317, 0.0727, 0.0197] _(grader stage 1)_

**[6] move_to** `{"x": 0.31790001457408523, "y": 0.07269985012791978, "z": 0.09, "pitch_deg": -90, "roll_deg": 101.9862770741368, "speed": 0.3}` → `{"rejected": true, "reason": "unreachable with pitch -90 deg (best IK error 9.6 mm / 18.7 deg). This position IS reachable with pitch_deg in [-70, -60, -50, -40, -30, -20, -10, 0, 10].", "sim_time_s": 5.9}` tip=[0.317, 0.0727, 0.0197] _(grader stage 1)_

**[7] move_to** `{"x": 0.31790001457408523, "y": 0.07269985012791978, "z": 0.09, "pitch_deg": -80, "roll_deg": 101.9862770741368, "speed": 0.3}` → `{"rejected": true, "reason": "unreachable with pitch -80 deg (best IK error 6.2 mm / 7.7 deg). This position IS reachable with pitch_deg in [-70, -60, -50, -40, -30, -20, -10, 0, 10].", "sim_time_s": 5.9}` tip=[0.317, 0.0727, 0.0197] _(grader stage 1)_

**[8] move_to** `{"x": 0.31790001457408523, "y": 0.07269985012791978, "z": 0.09, "pitch_deg": -70, "roll_deg": 101.9862770741368, "speed": 0.3}` → `{"completed": true, "sim_time_s": 7.58}` tip=[0.3178, 0.0728, 0.0897] _(grader stage 2)_

**[9] move_to** `{"x": 0.2526, "y": -0.0663, "z": 0.09, "pitch_deg": -90, "roll_deg": 101.9862770741368, "speed": 0.3}` → `{"rejected": true, "reason": "unreachable with pitch -90 deg (best IK error 8.5 mm / 4.3 deg). This position IS reachable with pitch_deg in [-80, -70, -60, -50, -40, -30, -20, -10, 0].", "sim_time_s": 7.58}` tip=[0.3178, 0.0728, 0.0897] _(grader stage 2)_

**[10] move_to** `{"x": 0.2526, "y": -0.0663, "z": 0.09, "pitch_deg": -80, "roll_deg": 101.9862770741368, "speed": 0.3}` → `{"completed": true, "sim_time_s": 9.1}` tip=[0.2525, -0.0662, 0.0898] _(grader stage 3)_

**[11] move_to** `{"x": 0.2526, "y": -0.0663, "z": 0.06, "pitch_deg": -90, "roll_deg": 101.9862770741368, "speed": 0.2}` → `{"completed": true, "sim_time_s": 10.14}` tip=[0.2524, -0.0662, 0.0598] _(grader stage 3)_

**[12] set_gripper** `{"opening": 1.0}` → `{"completed": true, "sim_time_s": 10.94}` tip=[0.2524, -0.0662, 0.0598] _(grader stage 4)_

**[13] move_relative** `{"dz": 0.04}` → `{"rejected": true, "reason": "unreachable with pitch -90 deg (best IK error 16.2 mm / 8.3 deg). This position IS reachable with pitch_deg in [-80, -70, -60, -50, -40, -30, -20, -10, 0].", "sim_time_s": 10.94}` tip=[0.2524, -0.0662, 0.0598] _(grader stage 4)_

**[14] finish** `{"success": true, "summary": "oracle script done"}` → `{"ok": true, "sim_time_s": 10.94}` _(grader stage 4)_

