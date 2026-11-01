**[1] set_gripper** `{"opening": 1.0}` → `{"completed": true, "sim_time_s": 0.8}` tip=[0.194, -0.0011, 0.0895] _(grader stage 0)_

**[2] move_to** `{"x": 0.2271, "y": -0.1876, "z": 0.07, "pitch_deg": -90, "roll_deg": 96.88122311952118, "speed": 0.5}` → `{"rejected": true, "reason": "unreachable with pitch -90 deg: best IK error 13.1 mm / 9.4 deg. Try a less steep pitch (e.g. -60 or -45) or a closer target.", "sim_time_s": 0.8}` tip=[0.194, -0.0011, 0.0895] _(grader stage 0)_

**[3] move_to** `{"x": 0.2271, "y": -0.1876, "z": 0.07, "pitch_deg": -80, "roll_deg": 96.88122311952118, "speed": 0.5}` → `{"completed": true, "sim_time_s": 3.3}` tip=[0.2271, -0.1875, 0.0698] _(grader stage 0)_

**[4] move_to** `{"x": 0.2271, "y": -0.1876, "z": 0.016957398276511944, "pitch_deg": -90, "roll_deg": 96.88122311952118, "speed": 0.2}` → `{"completed": true, "sim_time_s": 4.68}` tip=[0.2296, -0.191, 0.0271] _(grader stage 1)_

**[5] set_gripper** `{"opening": 0.0}` → `{"completed": true, "sim_time_s": 5.48}` tip=[0.2297, -0.1898, 0.0254] _(grader stage 1)_

**[6] move_to** `{"x": 0.2271, "y": -0.1876, "z": 0.09, "pitch_deg": -90, "roll_deg": 96.88122311952118, "speed": 0.3}` → `{"rejected": true, "reason": "unreachable with pitch -90 deg: best IK error 19.9 mm / 15.4 deg. Try a less steep pitch (e.g. -60 or -45) or a closer target.", "sim_time_s": 5.48}` tip=[0.2297, -0.1898, 0.0254] _(grader stage 1)_

**[7] move_to** `{"x": 0.2271, "y": -0.1876, "z": 0.09, "pitch_deg": -80, "roll_deg": 96.88122311952118, "speed": 0.3}` → `{"completed": true, "sim_time_s": 6.34}` tip=[0.2274, -0.1878, 0.0898] _(grader stage 2)_

**[8] move_to** `{"x": 0.2205, "y": -0.074, "z": 0.09, "pitch_deg": -90, "roll_deg": 96.88122311952118, "speed": 0.3}` → `{"completed": true, "sim_time_s": 8.08}` tip=[0.2205, -0.074, 0.0899] _(grader stage 3)_

**[9] move_to** `{"x": 0.2205, "y": -0.074, "z": 0.06, "pitch_deg": -90, "roll_deg": 96.88122311952118, "speed": 0.2}` → `{"completed": true, "sim_time_s": 9.08}` tip=[0.2205, -0.074, 0.0599] _(grader stage 3)_

**[10] set_gripper** `{"opening": 1.0}` → `{"completed": true, "sim_time_s": 9.88}` tip=[0.2205, -0.074, 0.0599] _(grader stage 4)_

**[11] move_relative** `{"dz": 0.04}` → `{"rejected": true, "reason": "unreachable with pitch -90 deg: best IK error 7.1 mm / 3.3 deg. Try a less steep pitch (e.g. -60 or -45) or a closer target.", "sim_time_s": 9.88}` tip=[0.2205, -0.074, 0.0599] _(grader stage 4)_

**[12] finish** `{"success": true, "summary": "oracle script done"}` → `{"ok": true, "sim_time_s": 9.88}` _(grader stage 4)_

