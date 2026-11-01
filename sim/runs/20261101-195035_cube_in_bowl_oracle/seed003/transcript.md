**[1] set_gripper** `{"opening": 1.0}` → `{"completed": true, "sim_time_s": 0.8}` tip=[0.194, -0.0011, 0.0895] _(grader stage 0)_

**[2] move_to** `{"x": 0.29969995790971987, "y": 0.041499920515729934, "z": 0.07, "pitch_deg": -90, "roll_deg": 62.096955377128914, "speed": 0.5}` → `{"rejected": true, "reason": "unreachable with pitch -90 deg (best IK error 9.8 mm / 6.0 deg). This position IS reachable with pitch_deg in [-80, -70, -60, -50, -40, -30, -20, -10, 0].", "sim_time_s": 0.8}` tip=[0.194, -0.0011, 0.0895] _(grader stage 0)_

**[3] move_to** `{"x": 0.29969995790971987, "y": 0.041499920515729934, "z": 0.07, "pitch_deg": -80, "roll_deg": 62.096955377128914, "speed": 0.5}` → `{"completed": true, "sim_time_s": 3.12}` tip=[0.2996, 0.0415, 0.0698] _(grader stage 0)_

**[4] move_to** `{"x": 0.29969995790971987, "y": 0.041499920515729934, "z": 0.016957398276012083, "pitch_deg": -90, "roll_deg": 62.096955377128914, "speed": 0.2}` → `{"completed": true, "sim_time_s": 4.44}` tip=[0.3009, 0.0413, 0.0195] _(grader stage 1)_

**[5] set_gripper** `{"opening": 0.0}` → `{"completed": true, "sim_time_s": 5.24}` tip=[0.3011, 0.0419, 0.0201] _(grader stage 1)_

**[6] move_to** `{"x": 0.29969995790971987, "y": 0.041499920515729934, "z": 0.09, "pitch_deg": -90, "roll_deg": 62.096955377128914, "speed": 0.3}` → `{"rejected": true, "reason": "unreachable with pitch -90 deg (best IK error 19.3 mm / 12.6 deg). This position IS reachable with pitch_deg in [-80, -70, -60, -50, -40, -30, -20, -10, 0].", "sim_time_s": 5.24}` tip=[0.3011, 0.0419, 0.0201] _(grader stage 1)_

**[7] move_to** `{"x": 0.29969995790971987, "y": 0.041499920515729934, "z": 0.09, "pitch_deg": -80, "roll_deg": 62.096955377128914, "speed": 0.3}` → `{"completed": true, "sim_time_s": 6.12}` tip=[0.2996, 0.0415, 0.0898] _(grader stage 2)_

**[8] move_to** `{"x": 0.1951, "y": -0.0864, "z": 0.09, "pitch_deg": -90, "roll_deg": 62.096955377128914, "speed": 0.3}` → `{"completed": true, "sim_time_s": 7.94}` tip=[0.1951, -0.0864, 0.0899] _(grader stage 3)_

**[9] move_to** `{"x": 0.1951, "y": -0.0864, "z": 0.06, "pitch_deg": -90, "roll_deg": 62.096955377128914, "speed": 0.2}` → `{"completed": true, "sim_time_s": 8.92}` tip=[0.1951, -0.0864, 0.0599] _(grader stage 3)_

**[10] set_gripper** `{"opening": 1.0}` → `{"completed": true, "sim_time_s": 9.72}` tip=[0.1951, -0.0864, 0.0599] _(grader stage 4)_

**[11] move_relative** `{"dz": 0.04}` → `{"completed": true, "sim_time_s": 10.6}` tip=[0.1979, -0.0882, 0.0999] _(grader stage 4)_

**[12] finish** `{"success": true, "summary": "oracle script done"}` → `{"ok": true, "sim_time_s": 10.6}` _(grader stage 4)_

