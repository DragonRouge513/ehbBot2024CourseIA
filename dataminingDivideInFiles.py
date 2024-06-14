import os
from os import walk
from os.path import join, splitext, basename

from html.parser import HTMLParser
from typing import List, Tuple

import re

import pandas as pd
import logging

logging.basicConfig(level = logging.INFO, format = '%(asctime)s - %(levelname)s - %(message)s')


class HTMLTextExtractor(HTMLParser):
	"""
	Extracts text content from HTML files, ignoring <style> and <script> tags.
	"""

	def __init__(self):
		super().__init__()
		self.text_content: List[str] = []
		self.ignore_tag: bool = False

	def handle_starttag(self, tag: str, attrs: List[Tuple[str, str]]) -> None:
		if tag in ["style", "script"]:
			self.ignore_tag = True

	def handle_endtag(self, tag: str) -> None:
		if tag in ["style", "script"]:
			self.ignore_tag = False

	def handle_data(self, data: str) -> None:
		if not self.ignore_tag:
			stripped_data = self.remove_special_characters(data.strip())
			if stripped_data:
				self.text_content.append(stripped_data)

	@property
	def extracted_text(self) -> List[str]:
		return self.text_content

	@staticmethod
	def remove_special_characters(data: str) -> str:
		return re.sub(r'\W+', ' ', data)


class HTMLFileHandler:
	"""
	Handles the processing of HTML files, including finding all HTML files in a directory and reading their contents.
	"""

	def __init__(self, directory: str):
		self.directory = directory
		self.file_paths = self.get_all_file_paths(self.directory)

	@staticmethod
	def get_all_file_paths(directory: str) -> List[str]:
		file_paths = []
		for root, _, files in walk(directory):
			for file in files:
				if file.endswith(".html"):
					file_paths.append(join(root, file))
		return file_paths

	@staticmethod
	def get_html_content(file_path: str) -> str:
		with open(file_path, encoding = "utf8") as file:
			return file.read()


class TextWriter:
	"""
	Writes the extracted text content to text files.
	"""

	@staticmethod
	def save_to_text(text_content: List[str], filename: str) -> None:
		directory = "txt"
		if not os.path.exists(directory):
			os.makedirs(directory)
		with open(join(directory, filename), 'w', encoding = 'utf-8') as file:
			for line in text_content:
				file.write(line + '\n')


def main():
	logging.info("Starting HTML text extraction and text writing")

	html_directory = 'htmlPages'
	html_file_handler = HTMLFileHandler(html_directory)
	text_writer = TextWriter()

	for file_path in html_file_handler.file_paths:
		logging.info(f"Processing file: {file_path}")
		html_content = html_file_handler.get_html_content(file_path)
		text_extractor = HTMLTextExtractor()
		text_extractor.feed(html_content)
		filename = splitext(basename(file_path))[0] + '.txt'
		text_writer.save_to_text(text_extractor.extracted_text, filename)
		text_extractor.text_content = []

	logging.info("HTML text extraction and text writing completed")


if __name__ == '__main__':
	main()
