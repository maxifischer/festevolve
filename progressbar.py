# module progressbar
import sys

def clear(lines):
	for _ in range(lines):
		sys.stdout.write("\033[F") #back to previous line
		sys.stdout.write("\033[K") #clear line

def draw(actual, target, width):
	if target <= 0:
		print actual
		return

	bar = "< "
	percent = actual/(target*1.0)
	for i in range(width):
		if i <= percent * width:
			bar += "-"
		else:
			bar += " "
	bar += " > "
	bar += str(actual) + " of " + str(target) + " (" + str(int(percent*100)) + "%)"
	print bar

def redraw(actual, target, width):
	clear(1)
	draw(actual,target,width)