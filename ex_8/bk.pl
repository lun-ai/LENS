
% BK of circuit graphs
% Circuit gates (AND gates with one input) labelled with numbers
gate(1).
gate(2).
gate(3).

% The output of ith gate is labelled with a symbol
out(0, src).
out(1, a).
out(2, b).
out(3, c).
out(4, light).

% Is Gate2 connected to gate Gate1?
is_connected(0, 1).
is_connected(1, 2).
is_connected(2, 3).
is_connected(3, 4).