
% BK of circuit graphs
% Circuit gates (AND gates with one input) labelled with numbers
gate(1).
gate(2).
gate(3).
gate(4).
gate(5).
gate(6).
gate(7).
gate(8).

% The output of ith gate is labelled with a symbol
out(0, src).
out(1, a).
out(2, b).
out(3, c).
out(4, d).
out(5, e).
out(6, f).
out(7, g).
out(8, h).
out(9, light).

% Is Gate2 connected to gate Gate1?
is_connected(0, 1).
is_connected(0, 2).
is_connected(1, 3).
is_connected(3, 4).
is_connected(2, 5).
is_connected(4, 6).
is_connected(5, 7).
is_connected(6, 8).
is_connected(8, 9).
is_connected(7, 9).