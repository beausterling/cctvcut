#!/usr/bin/env python3
"""Attach a returned sound carrier's audio to the unchanged cinematic picture.

Local files only. Requires ffmpeg/ffprobe. Makes no network/model calls.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def run(args):
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        raise ValueError(result.stderr.strip() or 'Command failed: ' + args[0])
    return result.stdout


def probe(path):
    return json.loads(run(['ffprobe', '-v', 'error', '-show_streams',
                           '-show_format', '-of', 'json', str(path)]))


def packet_hash(path, stream):
    return run(['ffmpeg', '-v', 'error', '-i', str(path), '-map', stream,
                '-c', 'copy', '-f', 'hash', '-hash', 'sha256', '-']).strip()


def duration_of(stream, info):
    value = stream.get('duration', info.get('format', {}).get('duration'))
    try:
        result = float(value)
    except (ValueError, TypeError):
        raise ValueError('Cannot establish stream duration; inspect the input.')
    if not math.isfinite(result) or result <= 0:
        raise ValueError('Input duration must be positive and finite.')
    return result


def assemble(original, carrier, output):
    original, carrier, output = [Path(p).expanduser().resolve()
                                 for p in (original, carrier, output)]
    archive = output.with_suffix('.audio.mka')
    manifest_path = output.with_suffix('.manifest.json')
    if output.suffix.lower() != '.mp4':
        raise ValueError('Use an .mp4 output path.')
    if not original.is_file() or not carrier.is_file():
        raise ValueError('Original and carrier must be existing files.')
    if original == carrier:
        raise ValueError('Use the original cinematic master and a separate carrier.')
    if any(p in (original, carrier) for p in (output, archive, manifest_path)):
        raise ValueError('Outputs must not overwrite either input.')
    if any(p.exists() for p in (output, archive, manifest_path)):
        raise ValueError('An output/archive/manifest already exists; choose a new name.')

    source_info, carrier_info = probe(original), probe(carrier)
    video = next((s for s in source_info['streams'] if s['codec_type'] == 'video'), None)
    audio = next((s for s in carrier_info['streams'] if s['codec_type'] == 'audio'), None)
    carrier_video = next((s for s in carrier_info['streams']
                          if s['codec_type'] == 'video'), None)
    if video is None:
        raise ValueError('Original has no video stream.')
    if audio is None:
        raise ValueError('Carrier has no audio stream.')
    target_duration = duration_of(video, source_info)
    audio_duration = duration_of(audio, carrier_info)
    end_gap = target_duration - audio_duration
    if end_gap > 0.001:
        raise ValueError(f'Carrier audio is {end_gap:.6f}s shorter than the cinematic '
                         'picture. No padding or stretching was applied; review timing.')
    audio_start = float(audio.get('start_time', 0) or 0)
    carrier_start = float((carrier_video or {}).get('start_time', 0) or 0)
    offset = audio_start - carrier_start
    if abs(offset) > 0.005:
        raise ValueError(f'Carrier audio/video start offset is {offset:.6f}s. '
                         'No silent timing correction was applied; review timing.')

    expected_video_hash = packet_hash(original, '0:v:0')
    expected_audio_hash = packet_hash(carrier, '0:a:0')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.genhq-assembly-',
                                     dir=str(output.parent)) as temp:
        temp = Path(temp)
        extracted, final = temp / 'extracted.mka', temp / 'final.mp4'
        run(['ffmpeg', '-v', 'error', '-n', '-i', str(carrier),
             '-map', '0:a:0', '-vn', '-c:a', 'copy', str(extracted)])
        if packet_hash(extracted, '0:a:0') != expected_audio_hash:
            raise ValueError('Extracted audio packet hash differs from the carrier.')
        # Only excess audio tail is trimmed. Video packets are copied, not encoded.
        # The unmodified encoded audio remains in the separate .audio.mka archive.
        run(['ffmpeg', '-v', 'error', '-n', '-i', str(original), '-i', str(carrier),
             '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy',
             '-af', f'atrim=duration={target_duration:.9f},asetpts=PTS-STARTPTS',
             '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', str(final)])
        actual_video_hash = packet_hash(final, '0:v:0')
        if actual_video_hash != expected_video_hash:
            raise ValueError('Video packet hash changed; final output rejected.')
        final_info = probe(final)
        final_video = next(s for s in final_info['streams'] if s['codec_type'] == 'video')
        final_audio = next(s for s in final_info['streams'] if s['codec_type'] == 'audio')
        for key in ('width', 'height', 'r_frame_rate', 'sample_aspect_ratio', 'nb_frames'):
            if key in video and final_video.get(key) != video[key]:
                raise ValueError('Original picture metadata changed: ' + key)
        run(['ffmpeg', '-v', 'error', '-i', str(final), '-f', 'null', '-'])
        data = {
            'original': str(original), 'carrier': str(carrier), 'output': str(output),
            'extracted_audio': str(archive), 'original_video_packets_unchanged': True,
            'video_packet_sha256': expected_video_hash,
            'extracted_audio_packet_sha256': expected_audio_hash,
            'target_duration_seconds': target_duration,
            'carrier_audio_duration_seconds': audio_duration,
            'sub_millisecond_endpoint_gap_seconds': max(0, end_gap),
            'carrier_audio_video_start_offset_seconds': offset,
            'audio_time_stretch_or_padding': False,
            'audio_processing': 'Excess tail trimmed if needed; delivery AAC encoded; no mastering or added sounds.',
            'final_audio': {k: final_audio.get(k) for k in
                            ('codec_name', 'sample_rate', 'channels', 'duration')},
            'listening_quality_verified': False,
        }
        os.replace(extracted, archive)
        os.replace(final, output)
        manifest_path.write_text(json.dumps(data, indent=2) + '\n')
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original', required=True, help='Original cinematic visual master')
    parser.add_argument('--carrier', required=True, help='Returned video/audio sound carrier')
    parser.add_argument('--output', required=True, help='New .mp4 path (must not exist)')
    args = parser.parse_args()
    try:
        result = assemble(args.original, args.carrier, args.output)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.exit(2, f'Assembly stopped: {exc}\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
