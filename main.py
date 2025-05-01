import os
import subprocess
import json

# Путь к распакованной папке ffmpeg
FFMPEG_PATH = r"C:\utils\ffmpeg\bin"


def get_video_duration(input_file):
    """Получение длительности видео в секундах."""
    ffprobe_path = os.path.join(FFMPEG_PATH, "ffprobe.exe")
    cmd = [
        ffprobe_path, '-v', 'quiet', '-print_format', 'json',
        '-show_format', input_file
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    data = json.loads(result.stdout)
    return float(data['format']['duration'])


def compress_video_to_size(input_file, output_file, target_size_mb):
    """Сжимает видео до указанного размера в МБ."""
    # Проверяем расширение выходного файла
    if not output_file.lower().endswith('.mp4'):
        output_file = os.path.splitext(output_file)[0] + '.mp4'
        print(f'Расширение выходного файла изменено на .mp4: {output_file}')

    # Преобразуем МБ в биты
    target_size_bits = target_size_mb * 8 * 1024 * 1024

    # Получаем длительность видео
    duration = get_video_duration(input_file)
    print(f"duration: {duration} sec")

    # Рассчитываем необходимый битрейт
    bitrate = int(target_size_bits * 0.95 / duration)
    print(f"bitrate: {bitrate} bps")

    ffmpeg_path = os.path.join(FFMPEG_PATH, "ffmpeg.exe")
    null_output = "NUL" if os.name == 'nt' else "/dev/null"

    # Первый проход
    cmd = [
        ffmpeg_path, '-i', input_file,
        '-c:v', 'libx264', '-b:v', f'{bitrate}',
        '-pass', '1', '-f', 'mp4', '-y', null_output
    ]
    subprocess.run(cmd)

    # Второй проход
    cmd = [
        ffmpeg_path, '-i', input_file,
        '-c:v', 'libx264', '-b:v', f'{bitrate}',
        '-pass', '2', '-c:a', 'aac', '-b:a', '128k',
        output_file
    ]
    subprocess.run(cmd)

    # Проверяем итоговый размер
    output_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f'Исходный файл: {input_file}')
    print(f'Сжатый файл: {output_file}')
    print(f'Целевой размер: {target_size_mb:.2f} МБ')
    print(f'Итоговый размер: {output_size_mb:.2f} МБ')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Сжатие видео до заданного размера')
    parser.add_argument('input', help='Путь к исходному видео')
    parser.add_argument('output', help='Путь для сохранения сжатого видео')
    parser.add_argument('size', type=float, help='Целевой размер в МБ')

    args = parser.parse_args()
    compress_video_to_size(args.input, args.output, args.size)