
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

% Is current flow detectable at an output when gate X is faulty?
flow(a, X) :- current(src, a, X).
flow(b, X) :- current(src, b, X).
flow(c, X) :- current(a, c, X).
flow(d, X) :- current(c, d, X).
flow(e, X) :- current(b, e, X).
flow(f, X) :- current(d, f, X).
flow(g, X) :- current(e, g, X).
flow(h, X) :- current(f, h, X).
on(light, X) :- current(h, light, X), current(g, light, X).