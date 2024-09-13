# -*- coding: utf-8 -*-

"""
Created on Thu Apr 18 11:34:26 2024

@author: Soumia
"""

import pygame
import pygame_gui
from pygame_gui.elements import UIHorizontalSlider, UIButton, UILabel
import time
import random

pygame.init()

# Window settings
window_size = (800 * 1.5, 500 * 1.5)
window = pygame.display.set_mode(window_size)
pygame.display.set_caption("Texture Evaluation")


manager = pygame_gui.UIManager(window_size, 'theme.json')

# Function to randomize slider start values
def randomize_start_values():
    return random.randint(1, 10), random.randint(1, 10)

# Initial random start values
start_value_roughness, start_value_vibration_intensity = randomize_start_values()


slider_roughness = UIHorizontalSlider(
    relative_rect=pygame.Rect(int(50 * 1.5), int(100 * 1.5), int(675 * 1.5), int(50 * 1.5)),
    start_value=start_value_roughness, value_range=(1, 10), manager=manager,
    object_id='slider_roughness')

slider_vibration_intensity = UIHorizontalSlider(
    relative_rect=pygame.Rect(int(50 * 1.5), int(250 * 1.5), int(675 * 1.5), int(50 * 1.5)),
    start_value=start_value_vibration_intensity, value_range=(1, 10), manager=manager,
    object_id='slider_vibration_intensity')


button_submit = UIButton(relative_rect=pygame.Rect(int(300 * 1.5), int(400 * 1.5), int(200 * 1.5), int(50 * 1.5)),
                         text='Submit', manager=manager)


label_roughness = UILabel(relative_rect=pygame.Rect(int(50 * 1.5), int(60 * 1.5), 300, 50),
                          text='Roughness:', manager=manager,
                          object_id='#label_roughness')

label_vibration_intensity = UILabel(relative_rect=pygame.Rect(int(50 * 1.5), int(210 * 1.5), 400, 50),
                                    text='Vibration Intensity:', manager=manager,
                                    object_id='#label_vibration_intensity')

# Labels for slider scale
label_smooth = UILabel(relative_rect=pygame.Rect(int(50 * 1.5), int(180 * 1.5), 150, 30),
                       text='Smooth (1)', manager=manager)

label_rough = UILabel(relative_rect=pygame.Rect(int(650 * 1.5), int(180 * 1.5), 150, 30),
                      text='Rough (10)', manager=manager)

label_texture_only = UILabel(relative_rect=pygame.Rect(int(50 * 1.5), int(330 * 1.5), 250, 30),
                             text='Texture alone (1)', manager=manager)

label_strong_vibration = UILabel(relative_rect=pygame.Rect(int(600 * 1.5), int(330 * 1.5), 250, 30),
                                 text='Very strong vibration (10)', manager=manager)


for i in range(1, 11):
    UILabel(relative_rect=pygame.Rect(int((65 + 70 * (i - 1)) * 1.5), int(150 * 1.5), 30, 30),
            text=str(i), manager=manager)

    UILabel(relative_rect=pygame.Rect(int((65 + 70 * (i - 1)) * 1.5), int(300 * 1.5), 30, 30),
            text=str(i), manager=manager)


results = []
participant_number = input("Enter participant number: ")
test_count = 0
nb_samples = 128 # depends on the test

clock = pygame.time.Clock()
is_running = True
show_timer = False

def draw_timer(seconds):
    start_ticks = pygame.time.get_ticks()
    while (pygame.time.get_ticks() - start_ticks) < (seconds * 1000):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
        
        window.fill(0)
        elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000
        fill_percentage = elapsed_time / seconds
        
        pygame.draw.circle(window, pygame.Color('#FFFFFF'), (int(400 * 1.5), int(300 * 1.5)), int(100 * 1.5), int(15 * 1.5))
        pygame.draw.arc(window, pygame.Color('#524040'), (int(300 * 1.5), int(200 * 1.5), int(200 * 1.5), int(200 * 1.5)),
                        -0.5 * 3.14159, (-0.5 + 2 * fill_percentage) * 3.14159, int(15 * 1.5))
        
        pygame.display.update()
        clock.tick(60)
    return True

while is_running:
    if show_timer and test_count > 0:  
        print(f'Test {test_count + 1}/{nb_samples}')
        if not draw_timer(6):
            break
        show_timer = False  
    
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
            break

        manager.process_events(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == button_submit:
                results.append((test_count + 1, slider_roughness.get_current_value(), slider_vibration_intensity.get_current_value()))
                test_count += 1

                if test_count < nb_samples:
                    show_timer = True  

                    # Randomize slider values for the next test
                    start_value_roughness, start_value_vibration_intensity = randomize_start_values()
                    slider_roughness.set_current_value(start_value_roughness)
                    slider_vibration_intensity.set_current_value(start_value_vibration_intensity)

              
                window.fill(0)
                pygame.display.update()
                waiting_for_keypress = True
                while waiting_for_keypress:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            waiting_for_keypress = False
                            is_running = False
                            break
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                            waiting_for_keypress = False

                if test_count >= nb_samples:
                    with open(f'Participant_{participant_number}.dat', 'w') as file:
                        file.write('Test\tRoughness\tVibration Intensity\n')
                        for test_number, roughness, vibration_intensity in results:
                            file.write(f'{test_number}\t{roughness}\t{vibration_intensity}\n')
                    is_running = False
                    break

        if not is_running:
            break

        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == slider_roughness or event.ui_element == slider_vibration_intensity:
                
                current_value = round(event.ui_element.get_current_value())
                event.ui_element.set_current_value(current_value)

    window.fill(0)

    manager.update(time_delta)
    manager.draw_ui(window)

    pygame.display.update()

pygame.display.quit()
pygame.quit()


