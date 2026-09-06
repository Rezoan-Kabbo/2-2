CSE 220 -- Signals and Linear Systems
January 2026 semester -- Offline: DFT & FFT
Due: Saturday 5 September, 1:00 PM

Read Jan2026_CSE220_Offline_DFT_FFT.pdf first; it is the specification.

You write
  transforms.py    shared transform core (naive DFT + radix-2 FFT + bonus)
  bigmul.py        Task A -- big-integer multiplication
  image_conv.py    Task B -- 2D convolution / image blur
Each is a runnable skeleton: every method you must fill in raises
NotImplementedError and carries a docstring stating exactly what it returns.
The two run_benchmark functions are already written -- they call your code
and produce the required runtime plots, so you only run them.

Provided -- do not modify
  io_utils.py      input files, reproducible random operands, report writing
  image_utils.py   image load/save, blur kernels, comparison figures
  bench_utils.py   timing helper and log-log runtime plots

Data
  inputs/          four Task A inputs (12, 200, 2048 and 20000 digits)
  images/          four sample images (see IMAGE_CREDITS.txt)

expected_outputs/  what a correct implementation produces
  task_a/1..4/     product.txt and report.txt
  task_a/benchmark/
  task_b/skyline_bokeh/          bokeh radius 9, FFT engine, colour
  task_b/sunset_motion/          motion length 41, FFT engine, grayscale
  task_b/skyline256_gaussian_dft/ the same pipeline driven by the naive DFT
  task_b/nebula_bokeh/           an extra example, not a required run
  task_b/benchmark/
The timings in these reports come from one particular machine. Your absolute
numbers will differ; the shapes of the curves should not.

Install:  pip install numpy matplotlib pillow
