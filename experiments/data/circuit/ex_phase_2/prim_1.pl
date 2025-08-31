gate(1).
gate(2).
gate(3).
gate(4).
gate(5).

test_point_label(1, output_a).
test_point_label(2, output_b).
test_point_label(3, output_c).
test_point_label(4, output_d).
test_point_label(5, output_e).

is_connected(0, 1).
is_connected(0, 2).
is_connected(1, 3).
is_connected(2, 3).
is_connected(3, 4).
is_connected(3, 5).
is_connected(4, lightbulb).
is_connected(5, lightbulb).