from PIL import Image

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