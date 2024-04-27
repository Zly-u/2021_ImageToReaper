import reapy
from PIL import Image
import os
import glob
import io
import time

print = reapy.print

DEBUG = False
proj_path = r"D:\ALL FOR PYCHARM\Projects\ImageToReaper"
images = glob.glob(proj_path + "\\images\\*.png")

im_from = 70
im_to = 147
images = images[im_from:im_to:]

time_start = time.time()
@reapy.inside_reaper()
def getImageInfo(image):
    image_data = Image.open(image)
    size = image_data.size

    pixel_data = []
    scaleX = 0.05
    scaleY = 0.05
    comp_scaleX = 1/scaleX
    comp_scaleY = 1/scaleY
    for y in range(int(size[1]*scaleY)):
        row = []
        for x in range(int(size[0]*scaleX)):
            row.append(
                image_data.getpixel((
                    int(x*comp_scaleX),
                    int(y*comp_scaleY)
                ))
            )
        pixel_data.append(row)
    return pixel_data
color_table = [
    [i for i in range(12)],
    [1, 4, 8, 13],
    [1, 6, 13],
    [5, 10],
    [8],
]
# def writeNotesInMidi(midi_take, clr):
#     index = 5-int((clr/255)*5)
#     if index == 0: return
#     print(index)
#     color = color_table[index-1]
#     for i in color:
#         midi_take.add_note(
#             0,
#             666,
#             i+30,
#             velocity=127, channel=0, selected=False, muted=False, unit="seconds", sort=False)

@reapy.inside_reaper()
def draw_image():
    image_info = getImageInfo(images[1])
    curProject = reapy.Project()

    MIDI_length = 1
    for yi, y in enumerate(image_info):
        midi_track = curProject.add_track(name="Time for ME to go to bed.", index=yi)
        for xi, x in enumerate(y):
            midi = midi_track.add_midi_item(start=xi * MIDI_length, end=(xi + 1) * MIDI_length, quantize=False)
            midi.set_info_value("I_CUSTOMCOLOR", reapy.rgb_to_native((x[0], x[1], x[2])) | 0x1000000)

@reapy.inside_reaper()
def videoRenderImage(midi_screen, processed_images_list):
    for image in processed_images_list:
        for yi, y in enumerate(image):
            for xi, x in enumerate(y):
                midi_screen[yi][xi].set_info_value("I_CUSTOMCOLOR", reapy.rgb_to_native((x[0], x[1], x[2])) | 0x1000000)
        return


@reapy.inside_reaper()
def makeFrames():
    curProject = reapy.Project()

    processed_images_list = []
    for image in images:
        processed_images_list.append(getImageInfo(image))

    width =  len(processed_images_list[0][0])
    height = len(processed_images_list[0])
    #make tracks
    if im_from == 0:
        for y in range(height):
            curProject.add_track(name="Time for ME to make video.", index=y)

    # prepare pixels(midis)
    '''
    30 fps = 1800 bpm -> lim 900 = 1800/2
    15 fps = 900 bpm
    -> init fps = 60 =>
    30 fps = 900 bpm
    init playRate 4
    init fps 60 * playrate
    '''
    playRate = 4
    bpm = 60 # 720
    fps = 30
    MIDI_length = ((1/fps)/width)*playRate

    midi_screen = []
    MIDI_frameOffsetStep = MIDI_length
    MIDI_frameOffset = (width*MIDI_frameOffsetStep)*im_from
    start_offset = 5
    for i, image in enumerate(processed_images_list):
        for yi, y in enumerate(image):
            midi_track = curProject.tracks[yi]
            row_x = []
            for xi, x in enumerate(y):
                midi = midi_track.add_midi_item(start=start_offset+MIDI_frameOffset + xi * MIDI_length, end=start_offset+MIDI_frameOffset + (xi + 1) * MIDI_length, quantize=False)
                midi.set_info_value("I_CUSTOMCOLOR", reapy.rgb_to_native((x[0], x[1], x[2])) | 0x1000000)
                row_x.append(midi)
            midi_screen.append(row_x)
        MIDI_frameOffset += width*MIDI_frameOffsetStep

@reapy.inside_reaper()
def getScreen():
    curProject = reapy.Project()
    tracks = curProject.tracks

    midi_screen = []
    for track in tracks:
        midi_screen.append(track.items)

    return midi_screen


@reapy.inside_reaper()
def play_video(midi_screen, processed_images_list):
    videoRenderImage(midi_screen, processed_images_list)

@reapy.inside_reaper()
def main():
    # curProject = reapy.Project()

    processed_images_list = []
    for image in images:
        processed_images_list.append(getImageInfo(image))

    # makeScreen()
    # play_video(getScreen(), processed_images_list)
    makeFrames()
    print(time.time()-time_start)

main()