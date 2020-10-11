from flask import current_app
from PIL import Image
import os
from os import listdir
from os.path import isfile, join

# Return a new image that is resized with black padding
def resize_image(img_file, background_color, width, height):
	img = Image.open(img_file)

	img_width, img_height = img.size

	screen_ratio = width / height
	img_ratio = img_width / img_height

	if img_ratio == screen_ratio:
		return img

	elif img_ratio > screen_ratio:
		new_height = height * img_width / width
		result = Image.new(img.mode, (img_width, int(new_height)), background_color)
		result.paste(img, ( 0, (int(new_height) - img_height) // 2 ) )
		return result

	elif img_ratio < screen_ratio:
		new_width = width * img_height / height
		result = Image.new(img.mode, (int(new_width), img_height), background_color)
		result.paste(img, ( (int(new_width) - img_width) // 2, 0))
		return result

def resize_all_images(new_width, new_height, id):
	# Check if resized directory exists
	# If not do nothing
	path = os.path.join(current_app.root_path, 'static', 'picture_files', str(id))
	re_path = os.path.join(current_app.root_path, 'static', 'picture_files', str(id), 'resized')
	if os.path.isdir(re_path):
		background_color = 'black'

		# Grab all files in the resized directory
		all_files = [f for f in listdir(re_path) if isfile(join(re_path, f))]
		for file in all_files:
			file_path = os.path.join(path, file)
			re_file_path = os.path.join(re_path, file)

			# Delete old resized image
			os.remove(re_file_path)

			# resize the original image
			re_img = resize_image(file_path, background_color, new_width, new_height)

			# Save the resized image
			re_img.save(re_file_path)