import contextlib
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOLS=Path(__file__).resolve().parents[1]/'archive_tools'
sys.path.insert(0,str(TOOLS))
import record_experiment as recorder

class RecordingWorkflow(unittest.TestCase):
    def test_commit_tag_overwrite_and_credential_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'history/experiments').mkdir(parents=True)
            for args in [('init','-b','main'),('config','user.name','Archive Test'),
                         ('config','user.email','test@example.invalid')]:
                subprocess.run(['git','-C',tmp,*args],check=True,capture_output=True)
            (root/'README.md').write_text('test\n',encoding='utf8')
            subprocess.run(['git','-C',tmp,'add','.'],check=True,capture_output=True)
            subprocess.run(['git','-C',tmp,'commit','-m','initial'],check=True,capture_output=True)
            note=root/'note.md';note.write_text('Real test result: known fixture.\n',encoding='utf8')
            config=root/'fixture.json';config.write_text('{"seed": 42}\n',encoding='utf8')
            args=['record','--id','fixture-01','--title','fixture','--kind','evaluation',
                  '--note-file',str(note),'--files','fixture.json']
            with patch.object(recorder,'ROOT',root),patch.object(sys,'argv',args),contextlib.redirect_stdout(io.StringIO()):
                recorder.main()
                refs=subprocess.check_output(['git','-C',tmp,'for-each-ref','--format=%(objecttype)','refs/tags'],text=True)
                self.assertEqual(refs.strip(),'tag')
                with self.assertRaises(ValueError):recorder.main()
            note.write_text(('pass'+'word')+'='+repr('test-placeholder')+'\n',encoding='utf8')
            args[args.index('fixture-01')]='fixture-02'
            with patch.object(recorder,'ROOT',root),patch.object(sys,'argv',args):
                with self.assertRaises(ValueError):recorder.main()
            self.assertEqual(subprocess.check_output(['git','-C',tmp,'rev-list','--count','HEAD'],text=True).strip(),'2')

if __name__=='__main__':unittest.main()
