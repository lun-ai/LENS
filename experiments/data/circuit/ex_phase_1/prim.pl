gate(1).
gate(2).
gate(3).
gate(4).
gate(5).
gate(6).

test_point_label(1, output_1).
test_point_label(2, output_2).
test_point_label(3, output_3).
test_point_label(4, output_4).
test_point_label(5, output_5).

is_connected(0, 1).
is_connected(0, 2).
is_connected(0, 3).
is_connected(1, 4).
is_connected(2, 5).
is_connected(3, 5).
is_connected(4, 6).
is_connected(4, lightbulb_x).
is_connected(6, lightbulb_y).