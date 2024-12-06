from aiogram import Router, F
import os
import logging
from pytubefix import YouTube, Playlist
from aiogram import Bot
from aiogram.types import Message
from aiogram.types.input_file import FSInputFile
from moviepy.editor import VideoFileClip
from pathlib import Path
from pytubefix.exceptions import PytubeFixError

logging.basicConfig(level=logging.INFO)

router = Router()

DOWNLOADS_PATH = Path('data/video')
AUDIO_PATH = Path('data/audio')
SPECIAL_SYMBOLS = ('\\', '/', ':', '*', '?', '"', '<', '>', '|', '#')

DOWNLOADS_PATH.mkdir(parents=True, exist_ok=True)
AUDIO_PATH.mkdir(parents=True, exist_ok=True)


@router.message(F.text.lower().in_(["хай", "хелоу", "привет", "ку"]))
async def greetings(message: Message):
    await message.reply("Привеееет!")


@router.message()
async def echo_url(message: Message, bot: Bot):
    if 'youtube.com/watch' in message.text or 'youtu.be' in message.text:
        await message.answer("Ссылка на YouTube получена.")
        try:
            file = FSInputFile(path=await handle_youtube(url=message.text))
            await bot.send_audio(chat_id=message.chat.id, audio=file)
        except Exception as e:
            await message.answer(f"Произошла ошибка")

    elif 'youtube.com/playlist' in message.text:
        await message.answer("Ссылка на YouTube плейлист получена.")
        playlist_link = message.text
        try:
            playlist = Playlist(playlist_link)
            for index, url in enumerate(playlist.video_urls, start=1):
                file = FSInputFile(path=await handle_youtube(url=url))
                await bot.send_audio(message.chat.id, audio=file)
                await message.answer(f"Видео {index}/{len(playlist.video_urls)} обработано.")
        except Exception as e:
            await message.answer(f"Произошла ошибка с плейлистом")

    await delete_files(DOWNLOADS_PATH)
    await delete_files(AUDIO_PATH)


async def handle_youtube(url):
    try:
        # Загрузка видео
        video = YouTube(url, use_oauth=True, allow_oauth_cache=True)
        title = video.title.lower()
        for symbol in SPECIAL_SYMBOLS:
            title = title.replace(symbol, '_')
        title_audio = AUDIO_PATH / f"{title}.mp3"

        # Скачивание видео
        video_stream = video.streams.first()
        if not video_stream:
            raise ValueError("Не удалось найти поток для скачивания.")
        
        original_filename = video_stream.default_filename
        clean_filename = "".join([c if c not in SPECIAL_SYMBOLS else "_" for c in Path(original_filename).stem]) + ".mp4"
        video_path = DOWNLOADS_PATH / clean_filename
        video_stream.download(output_path=DOWNLOADS_PATH, filename=clean_filename)

        # Проверяем существование файла
        logging.info(f"Скачано видео: {video_path}")
        if not video_path.exists():
            raise FileNotFoundError(f"Файл не найден: {video_path}")

        # Извлечение аудио
        with VideoFileClip(str(video_path)) as video_clip:
            audio = video_clip.audio
            audio.write_audiofile(filename=str(title_audio))
            logging.info(f"Аудио сохранено: {title_audio}")

        return str(title_audio)
    except Exception as e:
        logging.error(f"Общая ошибка обработки: {e}")
        raise RuntimeError(f"Ошибка обработки видео: {e}")
    finally:
        # Удаляем временный файл видео
        if video_path.exists():
            video_path.unlink()
            logging.info(f"Удалён файл: {video_path}")




async def delete_files(folder_path):
    files = os.listdir(folder_path)
    for file_name in files:
        file_path = Path(folder_path) / file_name
        if file_path.is_file():
            try:
                os.remove(file_path)
                logging.info(f"Удалён файл: {file_path}")
            except Exception as e:
                logging.error(f"Ошибка удаления файла {file_path}: {e}")
