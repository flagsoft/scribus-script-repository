## -- table_of_contents_with_chapter_numbers.py
## -- go through all text items in the document, check for heading styles and create a table of contents in the current text frame
## --
## -- © mit, ale rimoldi, 2023
## -- 2024, added chapter numbering (optional), from h1 to h10 flagsoft, mzm
##
## -- Usage
## 1. Select the text frame you have inserted for the table of contens to show
## 2. Script > Execute Script...
## 3. Choose this script table_of_contents.py
## 4. done. This may take some time, be patient.
## The new styles h1, h2, ... and toc1, toc2, ... will be generated autoamtically. You can and should change them later.
## Edit styles h1, h2, h3, etc. custom styles
## Edit styles toc1, ... custom styles, add 1 or 2 TABs, for chanpter numbering and/or page number at the right.
##
## -- Known issues and bugs
## chapter numbering bug
## at least Scribus version 1.6.1, Build ID: C--T-F-C1.17.6-Mac-64bit, Built: 7 January 2024.
## As it is, bug:
##   1.1       A
##   1.1.0.1   B   <-- note the zero, or this number is the last used, but it should be 1
##   1.?       C
## It should be:
##   1.1      A
##   1.1.1.1  B   <-- there is a virtual 1.1.1 chapter, this is correct
##   1.2      C
##

import sys

try:
		import scribus
except ImportError:
		print('This script must be run from inside Scribus')
		sys.exit()


## -- -------------------
## -- BEGIN user config
## --

## -- set this to False if you do not want chapter numbering
g_flag__chapter_numbering = True

## -- set custom style prefix
## note: it is a good practice to use a prefix for custom defined styles
g_prefix_str = ""   ## 'h1', ... and 'toc1', ...
#g_prefix_str = "_"   ## '_h1', ... and '_toc1', ...


heading_styles_base = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9', 'h10']
toc_styles_base     = ['toc1', 'toc2', 'toc3', 'toc4', 'toc5', 'toc6', 'toc7', 'toc8', 'toc9', 'toc10']

## -- how to handle newlines in headings
toc_new_lines = None       ## None     - no newline added
#toc_new_lines = strip     ## strip    - newlines will replaced by a single space character
#toc_new_lines = truncate  ## truncate - only the first part of heading til newline will be used

## -- you can use the item attributes to set the heading and toc styles
heading_attribute = 'heading_styles'
toc_attribute = 'toc_styles'
new_lines_attribute = 'toc_new_lines'

## --
## -- /END user config
## -- -------------------



## -- add optional prefix
## example "h1" -> "_h1"
heading_styles = [g_prefix_str + sub for sub in heading_styles_base] 
toc_styles = [g_prefix_str + sub for sub in toc_styles_base]



ui_chapter_level_1 = 0
ui_chapter_level_2 = 0
ui_chapter_level_3 = 0
ui_chapter_level_4 = 0
ui_chapter_level_5 = 0
ui_chapter_level_6 = 0
ui_chapter_level_7 = 0
ui_chapter_level_8 = 0
ui_chapter_level_9 = 0
ui_chapter_level_10 = 0
ui_chapter_level_11 = 0


# go through all paragraphs in the currently selected frame,
# and if the style is h1 add the paragraph to the list of headings
def get_frame_headings_by_style():
		headings = []
		paragraphs = scribus.getFrameText().split('\r')

		start = 0
		for p in paragraphs:
				scribus.selectFrameText(start, len(p))
				p_style = scribus.getParagraphStyle()
				start += len(p) + 1
				if p_style == None:
						continue
				if hasattr(scribus, 'currentPageNumberForSection'):
						# introduced in 1.5.9svn on 2023-01-25
						page_number = scribus.currentPageNumberForSection()
				else:
						page_number = scribus.currentPageNumber()

				if p_style in heading_styles:
						# remove frame (26) and column (27) breaks
						p = ''.join([c for c in p if ord(c) not in [26, 27]])
						# ignore empty lines (most of all if they only contain a frame break)
						if p == '':
								continue

						if toc_new_lines is not None:
								parts = p.split(chr(8232))
								if toc_new_lines == 'strip':
										p = ' '.join(parts)
								elif toc_new_lines == 'truncate':
										p = parts[0]
						headings.append({
								'title': p,
								'page': page_number,
								'level': heading_styles.index(p_style),
						})

		return headings

def main():
		global heading_styles, toc_styles, toc_new_lines
		global ui_chapter_level_1, ui_chapter_level_2, ui_chapter_level_3, ui_chapter_level_4, ui_chapter_level_5, ui_chapter_level_6, ui_chapter_level_7, ui_chapter_level_8, ui_chapter_level_9, ui_chapter_level_10, ui_chapter_level_11
		global g_flag__chapter_numbering

		if not scribus.haveDoc():
				return

		if scribus.selectionCount() == 0:
				return

		if scribus.getObjectType() != 'TextFrame':
				return

		toc_item = scribus.getSelectedObject()

		# read the heading and toc styles from the toc frame attributes
		for attribute in scribus.getObjectAttributes():
				if attribute['Name'] == heading_attribute:
						heading_styles = [style.strip() for style in attribute['Value'].split(',')]
				elif attribute['Name'] == toc_attribute:
						toc_styles = [style.strip() for style in attribute['Value'].split(',')]
				elif attribute['Name'] == new_lines_attribute:
						toc_new_lines = attribute['Value'].strip()
		# ensure that the styles exist
		for style in set(heading_styles + toc_styles).difference(scribus.getParagraphStyles()):
				scribus.createParagraphStyle(style)

		headings = []

		scribus.setRedraw(False)
		for page in range(1, scribus.pageCount() + 1):
				scribus.gotoPage(page)
				# get the text and linked frames, sorted by the position on the page
				page_text_frames = [(item[0], scribus.getPosition(item[0])) for item in scribus.getPageItems()
						if item[1] == 4]
				page_text_frames.sort(key= lambda item: (item[1][1], item[1][0]))

				for item, _ in page_text_frames:
						scribus.deselectAll()
						scribus.selectObject(item)
						headings += get_frame_headings_by_style()
		scribus.deselectAll()
		scribus.setRedraw(True)

		scribus.selectObject(toc_item)
		scribus.deleteText()
		start = 0

		for heading in headings:

				if start > 0:
						scribus.insertText('\r', -1)



				if (g_flag__chapter_numbering == False):

					## -- headings without chapter numbering
					scribus.insertText(heading['title'] + '\t' + str(heading['page']), -1)
					scribus.selectText(start, len(heading['title']))
					scribus.setParagraphStyle(toc_styles[heading['level']])
					start += len(heading['title']) + 1 + len(str(heading['page'])) + 1


				else:

					## -- headings with chapter numbering
					## 1
					##        <-- virtual chapter 1.1 here. (Scribus has bug it uses 1.0 here will end up in 1.0.1 or worse)
					## 1.1.1
					## 1.1.2
					## 1.2

					if ( heading['level'] == 0 ):
						ui_chapter_level_1 += 1
						ui_chapter_level_2 = 0
						ui_chapter_level_3 = 0
						ui_chapter_level_4 = 0
						ui_chapter_level_5 = 0
						ui_chapter_level_6 = 0
						ui_chapter_level_7 = 0
						ui_chapter_level_8 = 0
						ui_chapter_level_9 = 0
						ui_chapter_level_10 = 0

					if ( heading['level'] == 1 ):
						if ui_chapter_level_1 == 0: ui_chapter_level_1 = 1     ## virtual
						ui_chapter_level_2 += 1
						ui_chapter_level_3 = 0
						ui_chapter_level_4 = 0
						ui_chapter_level_5 = 0
						ui_chapter_level_6 = 0
						ui_chapter_level_7 = 0
						ui_chapter_level_8 = 0
						ui_chapter_level_9 = 0
						ui_chapter_level_10 = 0

					if ( heading['level'] == 2 ):
						if ui_chapter_level_1 == 0: ui_chapter_level_1 = 1     ## virtual
						if ui_chapter_level_2 == 0: ui_chapter_level_2 = 1     ## virtual
						ui_chapter_level_3 += 1
						ui_chapter_level_4 = 0
						ui_chapter_level_5 = 0
						ui_chapter_level_6 = 0
						ui_chapter_level_7 = 0
						ui_chapter_level_8 = 0
						ui_chapter_level_9 = 0
						ui_chapter_level_10 = 0

					if ( heading['level'] == 3 ):
						if ui_chapter_level_1 == 0: ui_chapter_level_1 = 1     ## virtual
						if ui_chapter_level_2 == 0: ui_chapter_level_2 = 1     ## virtual
						if ui_chapter_level_3 == 0: ui_chapter_level_3 = 1     ## virtual
						ui_chapter_level_4 += 1
						ui_chapter_level_5 = 0
						ui_chapter_level_6 = 0
						ui_chapter_level_7 = 0
						ui_chapter_level_8 = 0
						ui_chapter_level_9 = 0
						ui_chapter_level_10 = 0

					if ( heading['level'] == 4 ):
						if ui_chapter_level_1 == 0: ui_chapter_level_1 = 1     ## virtual
						if ui_chapter_level_2 == 0: ui_chapter_level_2 = 1     ## virtual
						if ui_chapter_level_3 == 0: ui_chapter_level_3 = 1     ## virtual
						if ui_chapter_level_4 == 0: ui_chapter_level_4 = 1     ## virtual
						ui_chapter_level_5 += 1
						ui_chapter_level_6 = 0
						ui_chapter_level_7 = 0
						ui_chapter_level_8 = 0
						ui_chapter_level_9 = 0
						ui_chapter_level_10 = 0

					if ( heading['level'] == 5 ):
						ui_chapter_level_6 += 1
						ui_chapter_level_7 = 0

					if ( heading['level'] == 6 ):
						ui_chapter_level_7 += 1
						ui_chapter_level_8 = 0

					if ( heading['level'] == 7 ):
						ui_chapter_level_8 += 1
						ui_chapter_level_9 = 0

					if ( heading['level'] == 8 ):
						ui_chapter_level_9 += 1
						ui_chapter_level_10 = 0

					if ( heading['level'] == 9 ):
						ui_chapter_level_10 += 1
						ui_chapter_level_11 = 0



					## 1.1.1.
					tmp_ui_heading_120_str = \
						str(ui_chapter_level_1) + '.' + \
						str(ui_chapter_level_2) + '.' + \
						str(ui_chapter_level_3) + '.' + \
						str(ui_chapter_level_4) + '.' + \
						str(ui_chapter_level_5) + '.' + \
						str(ui_chapter_level_6) + '.' + \
						str(ui_chapter_level_7) + '.' + \
						str(ui_chapter_level_8) + '.' + \
						str(ui_chapter_level_9) + '.' + \
						str(ui_chapter_level_10) + '.'

					## Remove the trailing characters if they are dot ('.'), or zero ('0')
					## 1.0.0.  -> 1
					## 1.2.    -> 1.2
					## 10.0.0. -> 10

					tmp_ui_heading_12_str = tmp_ui_heading_120_str.replace('.0', '')

					tmp_ui_heading_12_str = tmp_ui_heading_12_str.rstrip(".")  ## re move last dot

					#tmp_ui_heading_12_str = tmp_ui_heading_120_str.rstrip(".0")  ## does not work for "10." will give "1" instaed of "10"


					## 1.2.3<TAB><TITLE><TAB><PAGENUM>
					tmp_ui_heading_str = tmp_ui_heading_12_str + '\t' + heading['title'] + '\t' + str(heading['page'])
					scribus.insertText(tmp_ui_heading_str, -1)
					scribus.selectText(start, len(heading['title']))
					scribus.setParagraphStyle(toc_styles[heading['level']])  ## apply style
					start += len(tmp_ui_heading_str) + 1   ## calc starting position for next heading



		scribus.layoutText()

if __name__ == "__main__":
		main()
