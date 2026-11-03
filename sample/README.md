# Sample: OpenSpec

`openspec/` is a verbatim copy of the `openspec/` folder of [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec), taken at commit `2bd5bc3be964404657439f538857fcdf550f7398` (2026-11-02), under the MIT licence in `LICENSE`.
`sample.js` is generated from it by `build.py` (run `python3 sample/build.py [path-to-a-full-OpenSpec-clone]`; with a clone, each file's mtime is its last commit time up to that commit, and the OpenSpec version shown for the sample is read from the clone's `package.json` at that commit; without one, the version is left out) and is what the "Sample" option in `index.html` loads, via a script tag so it also works over `file://`.
