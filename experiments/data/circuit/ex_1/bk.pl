% Background knowledge of circuit
% Circuit gates (AND gates with multiple inputs) labelled with numbers
gate(1).
gate(2).
gate(3).
gate(4).

% The output of ith gate is labelled with a symbol
test_point_label(1, a).
test_point_label(2, b).
test_point_label(3, c).
test_point_label(4, d).

% Circuit connectivity
is_connected(0, 1).
is_connected(1, 2).
is_connected(1, 3).
is_connected(2, 4).
is_connected(3, 5).
is_connected(4, 5).