# -*- coding: utf-8 -*-

import os
import shutil
import pathlib


class Path(pathlib.Path):
    """
    @brief      提供基于pathlib的定制化文件路径操作
    """

    _flavour = type(pathlib.Path())._flavour

    def __new__(cls, *args, **kwargs):
        return pathlib.Path.__new__(cls, *args, **kwargs).resolve()

    def move_to(self, target_dir):
        """
        @brief      移动到指定目录

        @param      target_dir  目录路径

        @return     目标路径
        """
        target_dir = self.__class__(target_dir)
        if target_dir.exists() and target_dir.is_file():
            raise Exception('目标路径必须是文件夹')
        target_path = target_dir/self.name
        if target_path == self:
            pass
        else:
            if not target_dir.exists():
                target_dir.mkdirs()
            if self.is_file():
                if target_path.exists():
                    target_path.unlink()
                shutil.move(self, target_path)
            elif self.is_dir():
                if target_path.exists():
                    shutil.rmtree(target_path)
                shutil.move(self, target_path)
            else:
                raise Exception(f'{self}必须是文件或文件夹')
        return target_path

    def copy_to(self, target_dir):
        """
        @brief      复制到指定目录

        @param      target_dir  目录路径

        @return     目标路径
        """
        target_dir = self.__class__(target_dir)
        if target_dir.exists() and target_dir.is_file():
            raise Exception(f'{target_dir}必须是文件夹')
        target_path = target_dir/self.name
        if target_path == self:
            pass
        else:
            if not target_dir.exists():
                target_dir.mkdirs()
            if self.is_file():
                if target_path.exists():
                    target_path.unlink()
                shutil.copyfile(self, target_path)
            elif self.is_dir():
                if target_path.exists():
                    shutil.rmtree(target_path)
                shutil.copytree(self, target_path)
            else:
                raise Exception(f'{self}必须是文件或文件夹')
        return target_path

    def move_as(self, target_path):
        """
        @brief      移动为指定路径

        @param      target_path  目标路径

        @return     目标路径
        """
        target_path = self.__class__(target_path)
        if target_path == self:
            pass
        else:
            if not target_path.parent.exists():
                target_path.parent.mkdirs()
            if self.is_file():
                if target_path.exists():
                    target_path.unlink()
                shutil.move(self, target_path)
            elif self.is_dir():
                if target_path.exists():
                    shutil.rmtree(target_path)
                shutil.move(self, target_path)
            else:
                raise Exception(f'{self}必须是文件或文件夹')
        return target_path

    def copy_as(self, target_path):
        """
        @brief      复制为指定路径

        @param      target_path  目标路径

        @return     目标路径
        """
        target_path = self.__class__(target_path)
        if target_path == self:
            pass
        else:
            if not target_path.parent.exists():
                target_path.parent.mkdirs()
            if self.is_file():
                if target_path.exists():
                    target_path.unlink()
                shutil.copyfile(self, target_path)
            elif self.is_dir():
                if target_path.exists():
                    shutil.rmtree(target_path)
                shutil.copytree(self, target_path)
            else:
                raise Exception(f'{self}必须是文件或文件夹')
        return target_path

    @property
    def parent_names(self) -> list:
        """
        @brief      获取父目录名的列表

        @return     父目录名列表
        """
        parent_names = [i.name for i in self.parents]
        parent_names.remove('')
        return parent_names

    def file_list(self, extension=None, walk_mode=True, ignored_folders=None, parent_folder=None) -> list:
        """
        @brief      获取文件夹中文件的路径对象

        @param      extension        指定扩展名
        @param      walk_mode        是否查找子文件夹
        @param      ignored_folders  忽略文件夹列表，不遍历其子目录
        @param      parent_folder    父级文件夹，包含子目录

        @return     文件路径对象列表
        """
        if not self.is_dir():
            raise Exception(f'{self}必须是文件夹')
        file_path_ls = []
        for root, dirs, files in os.walk(self, topdown=True):
            root = self.__class__(root)
            if ignored_folders is not None:
                dirs[:] = [d for d in dirs if d not in ignored_folders]
            for file in files:
                file_path = root/file
                if extension is None:
                    file_path_ls.append(file_path)
                else:
                    if file_path.suffix.lower() == '.'+extension.lower():
                        file_path_ls.append(file_path)
            if walk_mode == False:
                break
        if parent_folder:
            file_path_ls = [file_path for file_path in file_path_ls if parent_folder in file_path.parent_names]
        return file_path_ls

    def folder_list(self):
        """
        @brief      获取文件夹内的子文件夹的路径

        @return     子文件夹路径列表
        """
        if not self.is_dir():
            raise Exception(f'{self}必须是文件夹')
        dir_path_ls = []
        for root, dirs, files in os.walk(self, topdown=True):
            root = self.__class__(root)
            for _dir in dirs:
                dir_path = root/_dir
                dir_path_ls.append(dir_path)
        return dir_path_ls

    def flat_folder_(self, del_folder=True) -> list:
        """
        @brief      将文件夹中子文件夹中的图片移动到自身文件夹根目录

        @param      del_folder  是否删除空文件夹

        @return     所有文件列表
        """
        if not self.is_dir():
            raise Exception(f'{self}必须是文件夹')
        flat_file_ls = [file.move_to(self) for file in self.file_list()]
        if del_folder:
            for i in self.iterdir():
                if i.is_dir():
                    shutil.rmtree(i)
        return flat_file_ls

    def flat_folder(self, output_folder) -> list:
        """
        @brief      将文件夹中子文件夹中的图片复制到指定文件夹根目录

        @param      output_folder  输出目录

        @return     所有目标文件列表
        """
        if not self.is_dir():
            raise Exception(f'{self}必须是文件夹')
        output_folder = self.__class__(output_folder)
        flat_file_ls = [file.copy_to(output_folder) for file in self.file_list()]
        return flat_file_ls

    def reio_path(self, input_folder, output_folder, mk_dir=False):
        """
        @brief      返回相对于输入文件夹目录结构在输出文件夹的路径

        @param      input_folder   输入文件夹路径
        @param      output_folder  输出文件夹路径
        @param      mk_dir         如果目标路径所在的目录不存在，则创建改目录

        @return     目标路径
        """
        input_folder = self.__class__(input_folder)
        output_folder = self.__class__(output_folder)
        target_path = output_folder/self.relative_to(input_folder)
        if mk_dir:
            if not target_path.parent.exists():
                target_path.parent.mkdirs()
        return target_path

    @property
    def to_str(self) -> str:
        """
        @brief      转化为字符串

        @return     字符串形式的路径
        """
        return str(self)

    def sweep(self):
        """
        @brief      清空文件夹
        """
        if not self.is_dir():
            raise Exception(f'{self}必须是文件夹')
        shutil.rmtree(self)
        self.mkdirs()

    def readbs(self, size=None) -> bytes:
        """
        @brief      读取指定长度字节，不指定长度则全部读取

        @param      size  长度

        @return     指定长度字节
        """
        with open(self, 'rb') as _f:
            _bytes = _f.read(size) if size is not None else _f.read()
        return _bytes

    def mkdirs(self):
        """
        @brief      创建多级目录，并防止并发时小概率因文件夹已存在的错误
        """
        self.mkdir(parents=True, exist_ok=True)
