from pathlib import Path
from re import sub
from shutil import move, unpack_archive
from sys import argv


ARCHIVES = {'.ZIP', '.GZ', '.TAR'}
AUDIO = {'.MP3', '.OGG', '.WAV', '.AMR'}
DOCUMENTS = {'.DOC', '.DOCX', '.TXT', '.PDF', '.XLSX', '.PPTX'}
IMAGES = {'.JPEG', '.PNG', '.JPG', '.SVG'}
VIDEO = {'.AVI', '.MP4', '.MOV', '.MKV'}
TRANS_MAP = {ord('а'): 'a', ord('А'): 'A', ord('б'): 'b', ord('Б'): 'B', ord('в'): 'v', ord('В'): 'V', ord('г'): 'g', ord('Г'): 'G', 
            ord('д'): 'd', ord('Д'): 'D', ord('е'): 'e', ord('Е'): 'E', ord('ё'): 'e', ord('Ё'): 'E', ord('ж'): 'j', ord('Ж'): 'J', 
            ord('з'): 'z', ord('З'): 'Z', ord('и'): 'i', ord('И'): 'I', ord('й'): 'j', ord('Й'): 'J', ord('к'): 'k', ord('К'): 'K', 
            ord('л'): 'l', ord('Л'): 'L', ord('м'): 'm', ord('М'): 'M', ord('н'): 'n', ord('Н'): 'N', ord('о'): 'o', ord('О'): 'O', 
            ord('п'): 'p', ord('П'): 'P', ord('р'): 'r', ord('Р'): 'R', ord('с'): 's', ord('С'): 'S', ord('т'): 't', ord('Т'): 'T', 
            ord('у'): 'u', ord('У'): 'U', ord('ф'): 'f', ord('Ф'): 'F', ord('х'): 'h', ord('Х'): 'H', ord('ц'): 'ts', ord('Ц'): 'TS', 
            ord('ч'): 'ch', ord('Ч'): 'CH', ord('ш'): 'sh', ord('Ш'): 'SH', ord('щ'): 'sch', ord('Щ'): 'SCH', ord('ъ'): '', ord('Ъ'): '', 
            ord('ы'): 'y', ord('Ы'): 'Y', ord('ь'): '', ord('Ь'): '', ord('э'): 'e', ord('Э'): 'E', ord('ю'): 'yu', ord('Ю'): 'YU', 
            ord('я'): 'ya', ord('Я'): 'YA', ord('є'): 'je', ord('Є'): 'JE', ord('і'): 'i', ord('І'): 'I', ord('ї'): 'ji', ord('Ї'): 'JI', 
            ord('ґ'): 'g', ord('Ґ'): 'G'}


file_list = {
    'images': [],
    'documents': [],
    'audio': [],
    'video': [],
    'archives': [],
    'unknown extensions': []
    }
known_extensions = set()
unknown_extensions = set()



def create_folder(path: Path, new_folder: str):
    
    try:
        Path.mkdir(path / new_folder, exist_ok=True)
    except FileExistsError:
        print(f'Папка {new_folder} уже существует в папке {path}')


def delete_folder(path: Path):
    
    try:
        path.rmdir()
    except FileNotFoundError:
        print(f'Невозможно удалить папку {path.name} т.к. её нет в папке {path.parent}')
    except OSError:
        print(f'Невозможно удалить папку {path.name} т.к. она не пустая')


def rename_file(file: Path) -> Path:

    file = Path(file)
    name_file = file.name.removesuffix(file.suffix)
    name_file = normalize(name_file)
    
    try:
        file = file.rename(file.parent.joinpath(name_file+file.suffix))
    except FileNotFoundError:
        print(f'Отсутствует файл {file} чтобы переименовать')
    except FileExistsError:
        print(f'Невозможно переименовать файл {file.name}, так как он уже существует в {file.parent}')

    
    return Path(file)


def rename_folder(folder: Path):

    try:
        folder.rename(folder.parent.joinpath(normalize(folder.name)))
    except FileNotFoundError:
        print(f'Невозможно переименовать папку {folder} на новую {normalize(folder.name)}')
    except PermissionError:
        print(f'Отказано в доступе к {folder}')





def folder_handling(folder: Path) -> bool:

    this_dir_empty = True

    for ff in folder.iterdir():

        # working with folders
        if ff.is_dir():
            if not (ff.name in {'images', 'documents', 'audio', 'video', 'archives'}):
                
                empty_dir = folder_handling(ff)
                if empty_dir:
                    delete_folder(ff)
                else:
                    rename_folder(ff)
                    this_dir_empty = False

            else:
                this_dir_empty = False
    
        # working with files
        else:
            
            this_dir_empty = False
            
            if ff.suffix.upper() in IMAGES:
                work_with_images(ff)            
            elif ff.suffix.upper() in VIDEO:
                work_with_video(ff)
            elif ff.suffix.upper() in DOCUMENTS:
                work_with_documents(ff)
            elif ff.suffix.upper() in AUDIO:
                work_with_audio(ff)
            elif ff.suffix.upper() in ARCHIVES:
                work_with_archives(ff)
            else:
                work_with_other(ff)
    
    return this_dir_empty


def move_file(file: Path, folder: str):
    
    file.parent.joinpath(folder).mkdir(exist_ok=True)

    if file.parent.joinpath(folder, file.name).exists():
        print(f'Файл {file.name} уже существует в папке {file.parent.joinpath(folder)}')
        return file
    
    return move(file, file.parent.joinpath(folder))


def work_with_archives(file: Path):

    file = rename_file(file)
    file_list['archives'].append(file.name)
    
    suffix_file = file.suffix.removeprefix('.')
    known_extensions.add(suffix_file.upper())
    
    name_folder = file.name.removesuffix(file.suffix)
    path_archives = file.parent.joinpath('archives', name_folder)
    
    path_archives.mkdir(exist_ok=True, parents=True)

    unpack_archive(file, path_archives)


def work_with_audio(file: Path):

    file = move_file(file, 'audio')
    file = rename_file(file)
    file_list['audio'].append(file.name)
    known_extensions.add(file.suffix.removeprefix('.').upper())


def work_with_documents(file: Path):

    file = move_file(file, 'documents')
    file = rename_file(file)
    file_list['documents'].append(file.name)
    known_extensions.add(file.suffix.removeprefix('.').upper())


def work_with_images(file: Path):

    file = move_file(file, 'images')
    file = rename_file(file)
    file_list['images'].append(file.name)
    known_extensions.add(file.suffix.removeprefix('.').upper())


def work_with_other(file: Path):
    file = rename_file(file)
    file_list['unknown extensions'].append(file.name)
    unknown_extensions.add(file.suffix.removeprefix('.').upper()) 


def work_with_video(file: Path):

    file = move_file(file, 'video')
    file = rename_file(file)
    file_list['video'].append(file.name)
    known_extensions.add(file.suffix.removeprefix('.').upper())


def normalize(string: str) -> str:

    string = string.translate(TRANS_MAP)
    
    return sub(r'\W', '_', string)


def output_file_list(file_list):

    lenght = 120
    print('='*(lenght+3))
    print('|{:^20}|{:^100}|'.format('Category', 'File'))
    print('='*(lenght+3))
    for category in file_list:
        
        for file in file_list[category]:
            print('|{:<20}|{:<100}|'.format(category, file))
        if len(file_list[category])>0:
            print('='*(lenght+3))

    if len(known_extensions) > 0:
        print('\nПеречень всех известных скрипту расширений, которые встречаются в целевой папке:')
        print(known_extensions)
        print('='*(lenght+3))
    if len(unknown_extensions) > 0:    
        print('Перечень всех расширений, которые скрипту неизвестны:')
        print(unknown_extensions)
        print('='*(lenght+3))


#===== M A I N =================================================================================================
if __name__ == '__main__':

    try:
        path = Path(argv[1])
    except IndexError:
        print('Не указана папка для сортировки')
    else:

        if path.exists() and path.is_dir:
            folder_handling(path)
            output_file_list(file_list)
        else:
            print('Путь к папке указан не корректно')