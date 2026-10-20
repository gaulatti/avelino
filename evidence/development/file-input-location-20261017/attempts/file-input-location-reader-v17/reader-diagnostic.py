import faulthandler, runpy, signal
from pathlib import Path
stream = Path('/probe/orca-stacks.log').open('w', buffering=1)
faulthandler.enable(file=stream,all_threads=True)
faulthandler.register(signal.SIGUSR1, file=stream, all_threads=True)
runpy.run_path('/usr/bin/orca', run_name='__main__')
