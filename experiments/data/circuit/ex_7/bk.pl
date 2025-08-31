% Background knowledge of circuit
% Circuit gates (AND gates with multiple inputs) labelled with numbers
gate(1).
gate(2).
gate(3).
gate(4).
gate(5).
gate(6).
gate(7).
gate(8).
gate(9).
gate(10).

% The output of ith gate is labelled with a symbol
test_point_label(1, a).
test_point_label(2, b).
test_point_label(3, c).
test_point_label(4, d).
test_point_label(5, e).
test_point_label(6, f).
test_point_label(7, g).
test_point_label(8, h).
test_point_label(9, i).
test_point_label(10, j).

% Circuit connectivity
is_connected(0, 1).
is_connected(1, 2).
is_connected(1, 3).
is_connected(2, 4).
is_connected(3, 5).
is_connected(0, 5).
is_connected(4, 6).
is_connected(2, 7).
is_connected(5, 7).
is_connected(5, 8).
is_connected(7, 9).
is_connected(9, 10).
is_connected(6, 11).
is_connected(10, 11).
is_connected(8, 11).