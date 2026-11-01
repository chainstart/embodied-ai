**[1] set_gripper** `{"opening": 1.0}` → `{"completed": true, "sim_time_s": 0.8}` tip=[0.194, -0.0011, 0.0895] _(grader stage 0)_

**[2] move_to** `{"x": 0.23720005345028858, "y": -0.029399945461595387, "z": 0.07, "pitch_deg": -90, "roll_deg": -67.47129949545604, "speed": 0.5}` → `{"completed": true, "sim_time_s": 2.68}` tip=[0.2371, -0.0294, 0.0698] _(grader stage 0)_

**[3] move_to** `{"x": 0.23720005345028858, "y": -0.029399945461595387, "z": 0.016957398276012076, "pitch_deg": -90, "roll_deg": -67.47129949545604, "speed": 0.2}` → `{"completed": true, "sim_time_s": 4.16}` tip=[0.2388, -0.0292, 0.019] _(grader stage 1)_

**[4] set_gripper** `{"opening": 0.0}` → `{"completed": true, "sim_time_s": 4.96}` tip=[0.2382, -0.0297, 0.0182] _(grader stage 1)_

**[5] move_to** `{"x": 0.23720005345028858, "y": -0.029399945461595387, "z": 0.09, "pitch_deg": -90, "roll_deg": -67.47129949545604, "speed": 0.3}` → `{"completed": true, "sim_time_s": 6.36}` tip=[0.237, -0.0294, 0.0898] _(grader stage 2)_

**[6] move_to** `{"x": 0.1823, "y": 0.1683, "z": 0.09, "pitch_deg": -90, "roll_deg": -67.47129949545604, "speed": 0.3}` → `{"rejected": true, "reason": "unreachable with pitch -90 deg: best IK error 4.6 mm / 2.3 deg. Try a less steep pitch (e.g. -60 or -45) or a closer target.", "sim_time_s": 6.36}` tip=[0.237, -0.0294, 0.0898] _(grader stage 2)_

**[7] move_to** `{"x": 0.1823, "y": 0.1683, "z": 0.09, "pitch_deg": -80, "roll_deg": -67.47129949545604, "speed": 0.3}` → `{"completed": true, "sim_time_s": 8.84}` tip=[0.1823, 0.1682, 0.0898] _(grader stage 3)_

**[8] move_to** `{"x": 0.1823, "y": 0.1683, "z": 0.06, "pitch_deg": -90, "roll_deg": -67.47129949545604, "speed": 0.2}` → `{"completed": true, "sim_time_s": 9.88}` tip=[0.1822, 0.1682, 0.0598] _(grader stage 3)_

**[9] set_gripper** `{"opening": 1.0}` → `{"completed": true, "sim_time_s": 10.68}` tip=[0.1822, 0.1682, 0.0598] _(grader stage 4)_

**[10] move_relative** `{"dz": 0.04}` → `{"rejected": true, "reason": "unreachable with pitch -90 deg: best IK error 12.5 mm / 6.2 deg. Try a less steep pitch (e.g. -60 or -45) or a closer target.", "sim_time_s": 10.68}` tip=[0.1822, 0.1682, 0.0598] _(grader stage 4)_

**[11] finish** `{"success": true, "summary": "oracle script done"}` → `{"ok": true, "sim_time_s": 10.68}` _(grader stage 4)_

