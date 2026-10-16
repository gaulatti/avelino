import importlib.util,json,subprocess,tempfile
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('capture',Path('scripts/capture-radio-cases.py'));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
with tempfile.TemporaryDirectory(prefix='avelino-radio-timeout-') as directory:
    output=Path(directory)/'captures'
    with patch.object(module.subprocess,'run',side_effect=subprocess.TimeoutExpired(['diagnostic-stub'],30)):
        try:module.capture(Path('/bin/true'),output)
        except AssertionError as error:print(type(error).__name__,str(error))
        else:raise AssertionError('Timeout was accepted')
    failure=json.loads((output/'failed-capture.json').read_text())
    assert failure['failure']=='timeout' and failure['timeoutSeconds']==30
    assert not failure['pngWritten'] and not failure['metadataWritten']
    assert (output/(failure['path']+'.log')).is_file()
    print('Injected subprocess timeout: fixed 30-second limit, failure status and raw log preserved; no GUI or visual acceptance claim')
