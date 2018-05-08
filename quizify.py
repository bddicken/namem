'''
Author: Benjamin Dicken
The purpose of this program is to convert a roster PDF file into various quizzing output formats.
The program takes a PDF file as input. In particular, it expects a class roster PDF file generated
by UAccess with images, names, and SIDS of the students.
This program expects a rather specific input document formatting.
It can produce either a quizzing web-application of a flashcard document.
'''

from wand.image import Image as WI
from PIL        import Image as PI
import numpy
import argparse
import os
import shutil

student_counter = 0

ROWS_PER_PAGE = 4
COLS_PER_PAGE = 4
MOSTLY_WHITE  = 0.9
LIGHT         = 255
DARK          = 0

def pixel_matches(pix, val):
    '''
    Returns true if the RGB values of the provided pixel (pix) all match the brightness value (val)
    '''
    return pix[0] == val and pix[1] == val and pix[2] == val

def get_y_of_next_person(page_pixels, current_x, current_y):
    '''
    Get's the y-value of the next persons photo on the page.
    page_pixels is a 3D list of all the pixels of a page.
    current_x and current_y is the location to begin looking for the next image at.
    '''
    y = current_y
    increment = 3
    while not pixel_matches(page_pixels[y][current_x], LIGHT):
        y += increment
    while pixel_matches(page_pixels[y][current_x], LIGHT) or pixel_matches(page_pixels[y][current_x], DARK):
        y += increment
    return y

def check_white_ratio(pil_img, ratio):
    '''
    Returns true if the ratio of all pixels to white pixels is greater than the specified ratio.
    pil_img is the PIL image object to check.
    ratio should be a number between 0.0 and 1.0.
    '''
    pixels = numpy.asarray(pil_img)
    white_count = 0.0
    total = 0.0
    for i in pixels:
        for j in i:
            total += 1.0
            if pixel_matches(j, LIGHT):
                white_count += 1.0
    return (white_count / total) > ratio

def grab_photos(page_img_file_name, page_num, rows, cols, quiz_dir):
    '''
    Extracts all of the photos and names from an image file.
    page_img_file_name is the name of the file to open and process.
    This should be an image file, not a PDF.
    page_num is the page number that the file was extracted from.
    rows and cols specifies the number of rows and columns of i
    student photos and names exists on the page.
    '''
    global student_counter
    FIRST_ROW_X_CHECK = 400
    NAME_OFFSET = 35
    start_x = 340
    width   = 410
    height  = 415
    spc_x   = 75
    spc_y   = 153
    page_img = PI.open(page_img_file_name)
    page_pixels = numpy.asarray(page_img)
    for y in range(rows):
        # First for-loop is for determining the y-coordinate of the photos in this row
        ty = 0
        for k in range(y+1):
            ty = get_y_of_next_person(page_pixels, FIRST_ROW_X_CHECK, ty)
        for x in range(cols):
            tx = start_x + ((width + spc_x) * x)
            # Grab student photo
            photo_img = page_img.crop((tx, ty, tx + width, ty + height))
            if not check_white_ratio(photo_img, MOSTLY_WHITE):
                photo_img.save(quiz_dir + '/photos/' + str(student_counter) + '.png')
                # Grab student name
                name_img = page_img.crop((tx-NAME_OFFSET,
                                      ty+height, 
                                      tx + width + (NAME_OFFSET*2),
                                      ty + height + spc_y))
                name_img.save(quiz_dir + '/names/' + str(student_counter) + '.png')
                student_counter += 1

def handle_args():
    '''
    Creates an argument parser and processes the arguments.
    Returns the arguments object to the caller.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('--roster', required=True, type=str, 
                        help='''A path to a PDF photo roster file, downloaded from uaccess.''')
    parser.add_argument('--quiz', required=True, type=str,
                        help='''A directory to place the resulting roster quiz in.
                              If the directory already exists, it will not generate the quiz,
                              unless --force is used.''')
    parser.add_argument('--force', default=False, action='store_true',
                        help='''If set, will overwrite the quiz output directory''')
    return parser.parse_args()

def check_output_directory_ok(args):
    return args.force or not os.path.exists(args.quiz)

def create_quiz_dir(args):
    if args.force and os.path.exists(args.quiz):
        try:
            shutil.rmtree(args.quiz)
        except:
            return False
    try:
        shutil.copytree('./template', args.quiz)
        os.makedirs(args.quiz + '/photos')
        os.makedirs(args.quiz + '/names')
    except:
        print('Failed to make new directories')
        return False
    return True

def main():
    args = handle_args()
    quiz_ok = check_output_directory_ok(args)
    if not quiz_ok:
        print('Quiz output directory already exists.')
        print('Choose different directory, or use --force to overwrite')
    else:
        if create_quiz_dir(args):
            im = WI(filename=args.roster, resolution=300)
            for i, page in enumerate(im.sequence):
                pi = WI(page)
                pi.alpha_channel = False
                page = './roster-' + str(i) + 's.png'
                pi.save(filename=page)
                grab_photos(page, i, ROWS_PER_PAGE, COLS_PER_PAGE, args.quiz)
                os.remove(page)

main()

