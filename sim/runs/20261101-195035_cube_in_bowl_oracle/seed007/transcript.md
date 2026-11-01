**[1] set_gripper** `{"opening": 1.0}` → `{"completed": true, "sim_time_s": 0.8}` tip=[0.194, -0.0011, 0.0895] _(grader stage 0)_

**[2] move_to** `{"x": 0.2641999915886715, "y": -0.13130003440060395, "z": 0.07, "pitch_deg": -90, "roll_deg": -103.73952792723715, "speed": 0.5}` → `{"rejected": true, "reason": "unreachable with pitch -90 deg (best IK error 13.0 mm / 9.0 deg). This position IS reachable with pitch_deg in [-80, -70, -60, -50, -40, -30, -20, -10, 0].", "sim_time_s": 0.8}` tip=[0.194, -0.0011, 0.0895] _(grader stage 0)_

**[3] move_to** `{"x": 0.2641999915886715, "y": -0.13130003440060395, "z": 0.07, "pitch_deg": -80, "roll_deg": -103.73952792723715, "speed": 0.5}` → `{"completed": true, "sim_time_s": 3.46}` tip=[0.2641, -0.1313, 0.0698] _(grader stage 0)_

**[4] move_to** `{"x": 0.2641999915886715, "y": -0.13130003440060395, "z": 0.016957398276028365, "pitch_deg": -90, "roll_deg": -103.73952792723715, "speed": 0.2}` → `{"completed": true, "sim_time_s": 4.82}` tip=[0.2679, -0.1327, 0.0262] _(grader stage 1)_

**[5] set_gripper** `{"opening": 0.0}` → `{"completed": true, "sim_time_s": 5.62}` tip=[0.267, -0.1329, 0.0251] _(grader stage 1)_

**[6] move_to** `{"x": 0.2641999915886715, "y": -0.13130003440060395, "z": 0.09, "pitch_deg": -90, "roll_deg": -103.73952792723715, "speed": 0.3}` → `{"rejected": true, "reason": "unreachable with pitch -90 deg (best IK error 20.3 mm / 15.1 deg). This position IS reachable with pitch_deg in [-80, -70, -60, -50, -40, -30, -20, -10, 0].", "sim_time_s": 5.62}` tip=[0.267, -0.1329, 0.0251] _(grader stage 1)_

**[7] move_to** `{"x": 0.2641999915886715, "y": -0.13130003440060395, "z": 0.09, "pitch_deg": -80, "roll_deg": -103.73952792723715, "speed": 0.3}` → `{"completed": true, "sim_time_s": 6.48}` tip=[0.2641, -0.1313, 0.0898] _(grader stage 2)_

**[8] move_to** `{"x": 0.2069, "y": 0.1606, "z": 0.09, "pitch_deg": -90, "roll_deg": -103.73952792723715, "speed": 0.3}` → `{"rejected": true, "reason": "unreachable with pitch -90 deg (best IK error 13.4 mm / 7.1 deg). This position IS reachable with pitch_deg in [-80, -70, -60, -50, -40, -30, -20, -10, 0].", "sim_time_s": 6.48}` tip=[0.2641, -0.1313, 0.0898] _(grader stage 2)_

**[9] move_to** `{"x": 0.2069, "y": 0.1606, "z": 0.09, "pitch_deg": -80, "roll_deg": -103.73952792723715, "speed": 0.3}` → `{"completed": true, "sim_time_s": 9.62}` tip=[0.2069, 0.1605, 0.0898] _(grader stage 3)_

**[10] move_to** `{"x": 0.2069, "y": 0.1606, "z": 0.06, "pitch_deg": -90, "roll_deg": -103.73952792723715, "speed": 0.2}` → `{"completed": true, "sim_time_s": 10.7}` tip=[0.2068, 0.1605, 0.0597] _(grader stage 3)_

**[11] set_gripper** `{"opening": 1.0}` → `{"completed": true, "sim_time_s": 11.5}` tip=[0.2068, 0.1605, 0.0598] _(grader stage 4)_

**[12] move_relative** `{"dz": 0.04}` → `{"rejected": true, "reason": "unreachable with pitch -90 deg (best IK error 20.3 mm / 11.1 deg). This position IS reachable with pitch_deg in [-80, -70, -60, -50, -40, -30, -20, -10, 0].", "sim_time_s": 11.5}` tip=[0.2068, 0.1605, 0.0598] _(grader stage 4)_

**[13] finish** `{"success": true, "summary": "oracle script done"}` → `{"ok": true, "sim_time_s": 11.5}` _(grader stage 4)_

