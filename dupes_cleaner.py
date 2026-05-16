"""
dupes-cleaner
- Remove arquivos indesejados
- Remove duplicados por hash
- Mantém o mais antigo
- Renomeia TODOS os arquivos
- Rename ocorre de dentro -> para fora
"""

from tkinter import Tk
from tkinter.filedialog import askdirectory
from pathlib import Path
import hashlib
import os
import uuid

CHUNK_SIZE = 4 * 1024 * 1024  # 4MB

EXTENSIONS_TO_DELETE = {
    ".jpeg",
    ".jpg",
    ".png",
    ".zip",
    ".rar",
    ".part"
}


def hash_file(path: Path) -> str:
    """Gera SHA-256 lendo em blocos."""
    hasher = hashlib.sha256()

    with path.open("rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            hasher.update(chunk)

    return hasher.hexdigest()


def get_age_key(path: Path):
    """
    Critério para manter duplicados:
    - mais antigo
    - desempate pelo path
    """
    stat = path.stat()

    if os.name == "nt":
        timestamp = stat.st_ctime
    else:
        timestamp = stat.st_mtime

    return (timestamp, str(path).lower())


def format_bytes(num_bytes: int) -> str:
    """Formata bytes."""
    units = ["B", "KB", "MB", "GB", "TB"]

    size = float(num_bytes)

    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.2f} {unit}"

        size /= 1024


def delete_unwanted_files(root_folder: Path):
    """Remove extensões indesejadas."""

    deleted = 0
    freed_space = 0

    print("\n[1/3] Removendo arquivos indesejados...\n")

    for path in root_folder.rglob("*"):

        if not path.is_file():
            continue

        if path.suffix.lower() not in EXTENSIONS_TO_DELETE:
            continue

        try:
            size = path.stat().st_size

            os.remove(path)

            deleted += 1
            freed_space += size

            print(f"[REMOVIDO] {path}")

        except OSError as e:
            print(f"[ERRO] {path}")
            print(e)

    print("\nArquivos removidos:")
    print(f"Total: {deleted}")
    print(f"Espaço liberado: {format_bytes(freed_space)}")


def scan_and_delete_duplicates(root_folder: Path):
    """Remove duplicados reais por hash."""

    print("\n[2/3] Verificando duplicados...\n")

    size_groups = {}

    deleted_count = 0
    duplicate_groups = 0
    saved_space = 0

    # agrupa por tamanho
    for path in root_folder.rglob("*"):

        if not path.is_file():
            continue

        try:
            size = path.stat().st_size
            size_groups.setdefault(size, []).append(path)

        except OSError:
            continue

    # hash apenas nos grupos relevantes
    for _, same_size_files in size_groups.items():

        if len(same_size_files) < 2:
            continue

        hash_groups = {}

        for path in same_size_files:
            try:
                file_hash = hash_file(path)
                hash_groups.setdefault(file_hash, []).append(path)

            except OSError:
                continue

        # remove duplicados
        for _, identical_files in hash_groups.items():

            if len(identical_files) < 2:
                continue

            ordered = sorted(
                identical_files,
                key=get_age_key
            )

            keep = ordered[0]
            remove = ordered[1:]

            duplicate_groups += 1

            print("\n[DUPLICADOS]")
            print(f"Mantido: {keep}")

            for file in remove:
                try:
                    size = file.stat().st_size

                    os.remove(file)

                    deleted_count += 1
                    saved_space += size

                    print(f"Removido: {file}")

                except OSError as e:
                    print(f"[ERRO] {file}")
                    print(e)

    print("\n" + "=" * 60)
    print("DUPLICADOS FINALIZADOS")
    print(f"Grupos: {duplicate_groups}")
    print(f"Arquivos removidos: {deleted_count}")
    print(f"Espaço liberado: {format_bytes(saved_space)}")
    print("=" * 60)


def rename_files_by_folder(root_folder: Path):
    """
    Rename de dentro -> fora.
    Arquivo maior vira (1).
    """

    print("\n[3/3] Renomeando arquivos...\n")

    # congela lista de pastas
    folders = [
        p for p in root_folder.rglob("*")
        if p.is_dir()
    ]

    # MAIS PROFUNDO PRIMEIRO
    folders.sort(
        key=lambda p: len(p.parts),
        reverse=True
    )

    # inclui pasta raiz no final
    folders.append(root_folder)

    for folder in folders:

        try:
            files = [
                f for f in folder.iterdir()
                if f.is_file()
            ]

        except OSError:
            continue

        if not files:
            continue

        # maior arquivo primeiro
        files.sort(
            key=lambda f: (
                -f.stat().st_size,
                f.name.lower()
            )
        )

        temp_files = []

        # FASE 1
        # nome temporário único
        for file in files:

            extension = file.suffix

            temp_name = (
                f"__tmp__"
                f"{uuid.uuid4().hex}"
                f"{extension}"
            )

            temp_path = folder / temp_name

            try:
                file.rename(temp_path)

                temp_files.append(temp_path)

            except OSError as e:
                print(f"[ERRO TEMP] {file}")
                print(e)

        # FASE 2
        folder_name = folder.name

        for index, temp_file in enumerate(
            temp_files,
            start=1
        ):
            new_name = (
                f"{folder_name} "
                f"({index})"
                f"{temp_file.suffix}"
            )

            final_path = folder / new_name

            try:
                temp_file.rename(final_path)

                print(
                    f"{temp_file.name} "
                    f"-> {new_name}"
                )

            except OSError as e:
                print(f"[ERRO FINAL] {temp_file}")
                print(e)


def main():
    root = Tk()
    root.withdraw()

    selected_folder = askdirectory(
        title="Selecione a pasta raiz"
    )

    root.destroy()

    if not selected_folder:
        print("Nenhuma pasta selecionada.")
        return

    root_folder = Path(selected_folder)

    if (
        not root_folder.exists()
        or not root_folder.is_dir()
    ):
        print("Pasta inválida.")
        return

    delete_unwanted_files(root_folder)
    scan_and_delete_duplicates(root_folder)
    rename_files_by_folder(root_folder)

    print("\nPROCESSO CONCLUÍDO")


if __name__ == "__main__":
    main()