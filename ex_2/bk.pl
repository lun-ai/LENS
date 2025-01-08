
% BK of circuit graphs
% Circuit gates (AND gates with one input) labelled with numbers
gate(1).
gate(2).
gate(3).
gate(4).
gate(5).

% The output of ith gate is labelled with a symbol
out(0, src).
out(1, a).
out(2, b).
out(3, c).
out(4, d).
out(5, e).
out(6, light).

% Is current flow detectable at an output when gate X is faulty?
flow(a, X) :- current(src, a, X).
flow(b, X) :- current(src, b, X).
flow(c, X) :- current(b, c, X), current(src, c, X).
flow(d, X) :- current(c, d, X), current(src, d, X).
flow(e, X) :- current(a, e, X), current(d, e, X).
on(light, X) :- current(e, light, X).