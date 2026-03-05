"""
dupes-cleaner: encontra duplicados por conteúdo, mantém o mais antigo e apaga o resto.
"""

from tkinter import Tk
from tkinter.filedialog import askdirectory
from pathlib import Path
import hashlib
import os

CHUNK_SIZE = 4 * 1024 * 1024  # 4 MB


def hash_file(path: Path) -> str:
    """Gera hash SHA-256 lendo o arquivo em blocos."""
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_age_key(path: Path):
    """
    Retorna a chave usada para decidir qual arquivo é o mais antigo.
    - Windows: usa data de criação (st_ctime)
    - Outros sistemas: usa data de modificação (st_mtime)
    Em empate, usa o caminho para desempate estável.
    """
    stat = path.stat()
    if os.name == "nt":
        timestamp = stat.st_ctime
    else:
        timestamp = stat.st_mtime

    return (timestamp, str(path).lower())


def format_bytes(num_bytes: int) -> str:
    """Formata bytes para leitura humana."""
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(num_bytes)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024


def scan_and_delete_duplicates(root_folder: Path):
    print(f"\nPasta raiz selecionada: {root_folder}")
    print("Mapeando arquivos...\n")

    size_groups = {}
    total_files = 0

    # 1) Agrupa por tamanho
    for path in root_folder.rglob("*"):
        if not path.is_file():
            continue

        try:
            size = path.stat().st_size
            size_groups.setdefault(size, []).append(path)
            total_files += 1
        except OSError as e:
            print(f"[ERRO] Não foi possível ler tamanho de: {path}")
            print(f"       Motivo: {e}")

    print(f"Total de arquivos encontrados: {total_files}")
    print(f"Grupos de tamanho analisados: {len(size_groups)}")
    print("\nIniciando verificação de duplicados...\n")

    deleted_count = 0
    duplicate_groups = 0
    saved_space = 0

    # 2) Só calcula hash para grupos com mais de 1 arquivo de mesmo tamanho
    for size, files_same_size in size_groups.items():
        if len(files_same_size) < 2:
            continue

        print(f"[TAMANHO] {len(files_same_size)} arquivo(s) com {size} bytes")

        hash_groups = {}

        for path in files_same_size:
            try:
                file_hash = hash_file(path)
                hash_groups.setdefault(file_hash, []).append(path)
                print(f"  [HASH] {path}")
            except OSError as e:
                print(f"  [ERRO] Falha ao ler: {path}")
                print(f"         Motivo: {e}")

        # 3) Para cada grupo idêntico, mantém o mais antigo e remove os demais
        for file_hash, identical_files in hash_groups.items():
            if len(identical_files) < 2:
                continue

            try:
                ordered_files = sorted(identical_files, key=get_age_key)
            except OSError as e:
                print(f"  [ERRO] Falha ao ordenar arquivos duplicados.")
                print(f"         Motivo: {e}")
                continue

            file_to_keep = ordered_files[0]
            files_to_delete = ordered_files[1:]
            duplicate_groups += 1

            print("\n  [DUPLICADOS ENCONTRADOS]")
            print(f"  Mantendo o mais antigo: {file_to_keep}")

            for dup in files_to_delete:
                try:
                    dup_size = dup.stat().st_size
                except OSError:
                    dup_size = 0

                try:
                    os.remove(dup)
                    deleted_count += 1
                    saved_space += dup_size
                    print(f"  Removido: {dup}")
                except OSError as e:
                    print(f"  [ERRO] Não foi possível remover: {dup}")
                    print(f"         Motivo: {e}")

            print()

    print("=" * 60)
    print("PROCESSO FINALIZADO")
    print(f"Grupos de duplicados encontrados: {duplicate_groups}")
    print(f"Arquivos removidos: {deleted_count}")
    print(f"Espaço liberado: {format_bytes(saved_space)}")
    print("=" * 60)


def main():
    root = Tk()
    root.withdraw()

    selected_folder = askdirectory(title="Selecione a pasta raiz")
    root.destroy()

    if not selected_folder:
        print("Nenhuma pasta foi selecionada.")
        return

    root_folder = Path(selected_folder)

    if not root_folder.exists() or not root_folder.is_dir():
        print("A pasta selecionada é inválida.")
        return

    scan_and_delete_duplicates(root_folder)


if __name__ == "__main__":
    main()