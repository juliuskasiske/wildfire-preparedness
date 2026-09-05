// The test I should have written. Calling onRequestPost directly proved the
// handler works but never proved Pages would route to it.
import * as mod from './submit.js';
const names = Object.keys(mod).filter(k => typeof mod[k] === 'function');
console.log('exported handlers:', names);
const bad = names.includes('onRequest') && names.some(n => /^onRequest(Get|Post|Put|Patch|Delete|Head|Options)$/.test(n));
console.log(bad
  ? 'FAIL  onRequest is exported alongside a method handler; it swallows every method'
  : 'pass  no generic onRequest, so onRequestPost is the handler Pages calls for POST');
process.exit(bad ? 1 : 0);
