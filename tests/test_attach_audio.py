"""Offline assembly tests. Requires ffmpeg and ffprobe; no model/API calls."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / 'skills/genhq-sound/scripts/attach_audio.py'
spec = importlib.util.spec_from_file_location('attach_audio', HELPER)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),
                     'FFmpeg and ffprobe are required')
class AttachAudioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='sound-skill-tests-',
                                               dir=os.environ.get('TMPDIR'))
        cls.folder = Path(cls.temp.name)
        cls.original = cls.folder / 'cinematic.mp4'
        cls.carrier = cls.folder / 'carrier.mp4'
        cls.short = cls.folder / 'short-carrier.mp4'
        helper.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i',
                    'testsrc2=size=320x180:rate=24:duration=2',
                    '-an', '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                    str(cls.original)])
        for target, audio_seconds in [(cls.carrier, 2), (cls.short, 0.5)]:
            helper.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i',
                        'color=blue:size=160x90:rate=24:duration=2',
                        '-f', 'lavfi', '-i', f'sine=frequency=440:duration={audio_seconds}',
                        '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'libx264',
                        '-pix_fmt', 'yuv420p', '-c:a', 'aac', str(target)])

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_success_preserves_original_picture_and_archives_audio(self):
        output = self.folder / 'success.mp4'
        data = helper.assemble(self.original, self.carrier, output)
        self.assertTrue(output.exists())
        self.assertTrue(data['original_video_packets_unchanged'])
        self.assertEqual(helper.packet_hash(self.original, '0:v:0'),
                         helper.packet_hash(output, '0:v:0'))
        self.assertEqual(helper.packet_hash(self.carrier, '0:a:0'),
                         helper.packet_hash(output.with_suffix('.audio.mka'), '0:a:0'))
        self.assertFalse(data['audio_time_stretch_or_padding'])
        self.assertFalse(data['listening_quality_verified'])
        manifest = json.loads(output.with_suffix('.manifest.json').read_text())
        self.assertEqual(manifest['output'], str(output.resolve()))
        video = next(s for s in helper.probe(output)['streams'] if s['codec_type'] == 'video')
        self.assertEqual(video['nb_frames'], '48')
        self.assertEqual((video['width'], video['height']), (320, 180))

    def test_short_audio_rejected_without_output(self):
        output = self.folder / 'short-result.mp4'
        with self.assertRaisesRegex(ValueError, 'shorter'):
            helper.assemble(self.original, self.short, output)
        self.assertFalse(output.exists())
        self.assertFalse(output.with_suffix('.audio.mka').exists())

    def test_missing_audio_rejected(self):
        silent_carrier = self.folder / 'silent-carrier.mp4'
        shutil.copyfile(self.original, silent_carrier)
        with self.assertRaisesRegex(ValueError, 'no audio'):
            helper.assemble(self.original, silent_carrier, self.folder / 'no-audio.mp4')

    def test_existing_output_not_overwritten(self):
        output = self.folder / 'existing.mp4'
        output.write_bytes(b'leave this alone')
        with self.assertRaisesRegex(ValueError, 'already exists'):
            helper.assemble(self.original, self.carrier, output)
        self.assertEqual(output.read_bytes(), b'leave this alone')

    def test_same_input_rejected(self):
        with self.assertRaisesRegex(ValueError, 'separate carrier'):
            helper.assemble(self.original, self.original, self.folder / 'same.mp4')

    def test_missing_input_rejected(self):
        with self.assertRaisesRegex(ValueError, 'existing files'):
            helper.assemble(self.folder / 'missing.mp4', self.carrier,
                            self.folder / 'missing-output.mp4')


if __name__ == '__main__':
    unittest.main()
