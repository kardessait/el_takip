import cv2
import mediapipe as mp
from mediapipe.python.solutions import hands as hands_module
from mediapipe.python.solutions import drawing_utils as mp_draw
import numpy as np
import math
import time




def main():
    hands = hands_module.Hands(
        max_num_hands=1,
        min_detection_confidence=0.8,
        min_tracking_confidence=0.8,
    )

    cap = cv2.VideoCapture(0)

    v_detected = False
    v_start_time = 0
    countdown_duration = 3

    drawing_segments = []
    current_segment = []
    drawing_color = (0, 255, 0)
    drawing_thickness = 5
    drawing_paused = True

    eraser_radius = 30
    eraser_color = (0, 0, 255)
    erasing_detected = False
    erasing_start_time = 0
    erasing_duration = 2

    selected_segment_index = -1
    drag_start_pos = None
    is_dragging = False
    drag_threshold = 40

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        black_screen = np.zeros((h, w, c), dtype=np.uint8)

        results = hands.process(rgb_frame)
        current_v_detected = False

        if results.multi_hand_landmarks:
            for hand_lms in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(black_screen, hand_lms, hands_module.HAND_CONNECTIONS)
                lms = hand_lms.landmark

                index_open = lms[8].y < lms[6].y
                middle_open = lms[12].y < lms[10].y
                ring_open = lms[16].y < lms[14].y
                pinky_open = lms[20].y < lms[18].y

                if index_open and not middle_open and not ring_open and not pinky_open and not is_dragging:
                    cx = int(lms[8].x * w)
                    cy = int(lms[8].y * h)
                    for _ in range(12):
                        spark_x = cx + np.random.randint(-20, 21)
                        spark_y = cy + np.random.randint(-20, 21)
                        spark_color = (np.random.randint(200, 256), np.random.randint(200, 256), np.random.randint(100, 256))
                        cv2.circle(black_screen, (spark_x, spark_y), 2, spark_color, -1)

                    current_segment.append((cx, cy))
                    if len(current_segment) > 200:
                        current_segment.pop(0)
                    drawing_paused = False
                elif not drawing_paused:
                    if len(current_segment) > 1:
                        drawing_segments.append(current_segment.copy())
                        if len(drawing_segments) > 50:
                            drawing_segments.pop(0)
                    current_segment = []
                    drawing_paused = True

                if not index_open and middle_open and not ring_open and not pinky_open:
                    eraser_x = int(lms[12].x * w)
                    eraser_y = int(lms[12].y * h)
                    if not erasing_detected:
                        erasing_detected = True
                        erasing_start_time = time.time()

                    elapsed_erasing_time = time.time() - erasing_start_time
                    remaining_erasing_time = max(0, erasing_duration - elapsed_erasing_time)

                    if remaining_erasing_time > 0:
                        cv2.putText(black_screen, f"Silme: {int(remaining_erasing_time + 1)} saniye", 
                                   (50, h // 2 - 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        cv2.circle(black_screen, (eraser_x, eraser_y), eraser_radius, eraser_color, 3)
                    else:
                        explosion_particles = []
                        new_segments = []
                        for segment in drawing_segments:
                            new_segment = []
                            for point in segment:
                                distance = math.hypot(point[0] - eraser_x, point[1] - eraser_y)
                                if distance > eraser_radius:
                                    new_segment.append(point)
                                else:
                                    for _ in range(3):
                                        particle_x = point[0] + np.random.randint(-20, 21)
                                        particle_y = point[1] + np.random.randint(-20, 21)
                                        particle_color = (np.random.randint(0, 256), np.random.randint(0, 256), np.random.randint(0, 256))
                                        explosion_particles.append((particle_x, particle_y, particle_color))
                            if new_segment:
                                new_segments.append(new_segment)

                        if current_segment:
                            new_current = []
                            for point in current_segment:
                                distance = math.hypot(point[0] - eraser_x, point[1] - eraser_y)
                                if distance > eraser_radius:
                                    new_current.append(point)
                                else:
                                    for _ in range(3):
                                        particle_x = point[0] + np.random.randint(-20, 21)
                                        particle_y = point[1] + np.random.randint(-20, 21)
                                        particle_color = (np.random.randint(0, 256), np.random.randint(0, 256), np.random.randint(0, 256))
                                        explosion_particles.append((particle_x, particle_y, particle_color))
                            current_segment = new_current

                        drawing_segments = new_segments
                        for particle in explosion_particles:
                            cv2.circle(black_screen, (particle[0], particle[1]), 2, particle[2], -1)
                        erasing_detected = False
                else:
                    erasing_detected = False

                if index_open and not middle_open and not ring_open and pinky_open:
                    explosion_particles = []
                    for segment in drawing_segments:
                        for point in segment:
                            for _ in range(5):
                                particle_x = point[0] + np.random.randint(-30, 31)
                                particle_y = point[1] + np.random.randint(-30, 31)
                                particle_color = (np.random.randint(0, 256), np.random.randint(0, 256), np.random.randint(0, 256))
                                explosion_particles.append((particle_x, particle_y, particle_color))
                    for point in current_segment:
                        for _ in range(5):
                            particle_x = point[0] + np.random.randint(-30, 31)
                            particle_y = point[1] + np.random.randint(-30, 31)
                            particle_color = (np.random.randint(0, 256), np.random.randint(0, 256), np.random.randint(0, 256))
                            explosion_particles.append((particle_x, particle_y, particle_color))
                    for particle in explosion_particles:
                        cv2.circle(black_screen, (particle[0], particle[1]), 2, particle[2], -1)
                    drawing_segments.clear()
                    current_segment.clear()
                    cv2.putText(black_screen, "Hizli Silme: Cizimler Temizlendi!", (50, h // 2), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 255), 3)

                if index_open and middle_open and not ring_open and not pinky_open:
                    dist = math.hypot(lms[8].x - lms[12].x, lms[8].y - lms[12].y)
                    if dist > 0.08:
                        current_v_detected = True
                        if not v_detected:
                            v_detected = True
                            v_start_time = time.time()
                        break

                thumb_x = int(lms[4].x * w)
                thumb_y = int(lms[4].y * h)
                pinky_x = int(lms[20].x * w)
                pinky_y = int(lms[20].y * h)
                thumb_pinky_dist = math.hypot(thumb_x - pinky_x, thumb_y - pinky_y)

                if thumb_pinky_dist < drag_threshold:
                    if not is_dragging:
                        selected_segment_index = -1
                        min_dist_to_segment = float('inf')
                        for idx, segment in enumerate(drawing_segments):
                            for point in segment:
                                dist_to_point = math.hypot(thumb_x - point[0], thumb_y - point[1])
                                if dist_to_point < min_dist_to_segment:
                                    min_dist_to_segment = dist_to_point
                                    selected_segment_index = idx
                        if selected_segment_index >= 0 and min_dist_to_segment < 50:
                            is_dragging = True
                            drag_start_pos = (thumb_x, thumb_y)
                    else:
                        if selected_segment_index >= 0 and selected_segment_index < len(drawing_segments) and drag_start_pos:
                            current_pos = (thumb_x, thumb_y)
                            offset_x = current_pos[0] - drag_start_pos[0]
                            offset_y = current_pos[1] - drag_start_pos[1]
                            new_segment = []
                            for point in drawing_segments[selected_segment_index]:
                                new_x = point[0] + offset_x
                                new_y = point[1] + offset_y
                                new_x = max(0, min(w-1, new_x))
                                new_y = max(0, min(h-1, new_y))
                                new_segment.append((new_x, new_y))
                            drawing_segments[selected_segment_index] = new_segment
                            drag_start_pos = current_pos
                else:
                    is_dragging = False
                    selected_segment_index = -1
                    drag_start_pos = None

        for idx, segment in enumerate(drawing_segments):
            if len(segment) > 1:
                is_selected = idx == selected_segment_index and is_dragging
                segment_color = (255, 255, 180) if is_selected else ((255, 165, 0) if idx == selected_segment_index else drawing_color)
                segment_thickness = 10 if is_selected else (8 if idx == selected_segment_index else drawing_thickness)
                for i in range(1, len(segment)):
                    cv2.line(black_screen, segment[i-1], segment[i], segment_color, segment_thickness)
                    if is_selected and i % 5 == 0:
                        glow_x = segment[i][0]
                        glow_y = segment[i][1]
                        cv2.circle(black_screen, (glow_x, glow_y), 6, (255, 255, 200), -1)

                if is_selected:
                    for _ in range(15):
                        spark_x = segment[np.random.randint(len(segment))][0]
                        spark_y = segment[np.random.randint(len(segment))][1]
                        spark_color = (np.random.randint(220, 256), np.random.randint(220, 256), np.random.randint(150, 256))
                        cv2.circle(black_screen, (spark_x, spark_y), 3, spark_color, -1)

        if len(current_segment) > 1:
            for i in range(1, len(current_segment)):
                cv2.line(black_screen, current_segment[i-1], current_segment[i], drawing_color, drawing_thickness)

        if v_detected:
            elapsed_time = time.time() - v_start_time
            remaining_time = max(0, countdown_duration - elapsed_time)
            if current_v_detected and remaining_time > 0:
                cv2.putText(black_screen, f"V Algilandi! {int(remaining_time + 1)} saniye sonra kapanacak", 
                            (50, h // 2 - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            elif current_v_detected and remaining_time <= 0:
                cv2.putText(black_screen, "Sistem Kapatiliyor...", (50, h // 2), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
                cv2.imshow("M4 Mac - Neon Hand Tracking", black_screen)
                cv2.waitKey(1000)
                cap.release()
                cv2.destroyAllWindows()
                exit()
            else:
                v_detected = False

        cv2.imshow("M4 Mac - Neon Hand Tracking", black_screen)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
