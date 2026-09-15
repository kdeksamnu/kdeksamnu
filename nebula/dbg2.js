const N = require('./core.js');
const net = new N.MLP([2, 4, 1], 1);
console.log('sizes', net.sizes, 'W layers', net.W.length);
net.W[0].set([1, 0, 0, 1, 1, 1, -1, -1]);
net.b[0].set([0, 0, 0, 0]);
net.W[1].set([1, 1, 1, 1]);
net.b[1].set([0]);
const out = new Float32Array(1);
const r = net.forward(new Float32Array([0.5, 0.25]), out);
console.log('forward returned:', r, '| out buffer:', Array.from(out));
console.log('expected 1.5  (relu([0.5,0.25,0.75,-0.75]) summed)');

// also test step() on a known-gradient case
const net2 = new N.MLP([1, 1], 1);
net2.W[0].set([2]); net2.b[0].set([0]);
const l = net2.step(new Float32Array([1]), new Float32Array([0]), 0.0); // lr=0 -> no update
console.log('loss (pred=2, target=0):', l, 'expected 4');