import win32com.client as client
from os import path
import rarfile
import zipfile
from comtypes import client
import pikepdf
import itertools


class PassCracker:
    def __init__(self, document, password_list, bottom, up):
        self.document = document
        self.password_list = password_list
        self.alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        self.bottom = bottom
        self.up = up

    @staticmethod
    def find_pos(symbols, string):
        return sum(len(symbols) ** (len(string) - p) * symbols.index(s) for p, s in enumerate(string, 1))

    def attempt(self, password):
        if self.document[self.document.rindex("."):] == ".xlsx":
            try:
                excel = client.Dispatch("Excel.Application")
                wb = excel.Workbooks.Open(
                    path.abspath(self.document),
                    False,
                    True,
                    None,
                    password
                )
                wb.Close()
                excel.Quit()
                return True
            except Exception as exception:
                print(exception)
                pass
        if self.document[self.document.rindex("."):] == ".rar":
            try:
                rar_archive = rarfile.RarFile(path.abspath(self.document))
                rar_archive.extractall(pwd=password)
                rar_archive.close()
                return True
            except Exception as exception:
                print(exception)
                pass
        if self.document[self.document.rindex("."):] == ".zip":
            try:
                zip_archive = zipfile.ZipFile(path.abspath(self.document))
                zip_archive.extractall(pwd=password.encode("ascii"))
                zip_archive.close()
                return True
            except Exception as exception:
                print(exception)
                pass
        if self.document[self.document.rindex("."):] == ".docx":
            try:
                word_doc = client.CreateObject("Word.Application")
                a = word_doc.Documents.Open(
                    path.abspath(self.document),
                    False,
                    True,
                    None,
                    password)
                a.Close()
                word_doc.Quit()
                return True
            except Exception as exception:
                print(exception)
                pass
        if self.document[self.document.rindex("."):] == ".pdf":
            try:
                with pikepdf.open(path.abspath(self.document), password=password):
                    return True
            except Exception as exception:
                print(exception)
                pass
        return False

    def crack_password(self):
        if self.password_list:
            with open(path.abspath(self.password_list), "r") as wordlist:
                for word in wordlist.readlines():
                    password = word.replace("\n", "")
                    if self.attempt(password):
                        return f"Hey, I found the correct password. Here it is ['{password}']"
                return f"Oh I couldn't find the password"
        else:
            for i in range(self.bottom, self.up + 1):
                start_string = 'a'*i
                gen = itertools.product(self.alphabet, repeat=i)
                for password in itertools.islice(
                        gen,
                        self.find_pos(self.alphabet, start_string),
                        len(self.alphabet) ** i):
                    password = ''.join(password)
                    if self.attempt(password):
                        return f"Hey, I found the correct password. Here it is ['{password}']"
            return f"Oh I couldn't find the password"
