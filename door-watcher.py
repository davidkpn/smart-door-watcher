import numpy as np
import cv2
import time
import face_recognition
import dataset_generator as ds

# to install the face_reco, the following steps required:
#   1. git clone https://github.com/davisking/dlib.git ( download the dlib directory from git )
#   2. pip install cmake ( install the cmake library from pip )
#   3. cd dlib; python3 setup.py install
#   4. pip install face_recognition

cap = cv2.VideoCapture(0)
ret, prev_frame = cap.read()
motion_capture = True
font = cv2.FONT_HERSHEY_DUPLEX
height, width = prev_frame.shape[:2]

# output file
# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
out = cv2.VideoWriter()
start_timer = 0

# load known people
known_face_names = ds.known_face_names
known_face_encodings = ds.known_face_encodings

# while connected
while(ret):
    ret ,frame = cap.read()

    if motion_capture:
        substracted = cv2.subtract(prev_frame, frame)
        substracted_grayscaled = cv2.cvtColor(substracted, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(substracted_grayscaled, 0, 255, cv2.THRESH_BINARY)

        # calculation
        white_pixels = len(thresh[thresh == 255]) # np.sum(thresh) / 255
        white_percentage = white_pixels / thresh.size # (height*width)

        if white_percentage > 0.1: # movement detected
            motion_capture = False
            out = cv2.VideoWriter("./videos/{}.avi".format( time.strftime("%Y-%m-%d %H-%M-%S", time.gmtime(time.time())) ) ,fourcc, 20.0, (width, height))
            start_timer = time.time()
        else:
            # sleeping for battery power saving
            time.sleep(.5)

    # motion detector
    if not motion_capture:
            # 1) find object
            # 2) live stream the frames
            # 3) record until object is out of screen

            # frame processing every 3 frames
            if int(out.get(cv2.CAP_PROP_FRAME_COUNT)) % 3 == 0 :
                # Resize frame of video to 1/4 size for faster face recognition processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
                rgb_small_frame = small_frame[:, :, ::-1]

                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                face_names = []
                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    index = next(i for i, kpe in enumerate(face_recognition) if face_recognition.compare_faces([kpe], face_encoding)[0])

                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = 'Unknown'
                    # If a match was found in known_face_encodings, just use the first one.
                    if index:
                        name = known_face_names[index]

                    face_names.append(name)

            # Display the results
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                if name == 'Unknown':
                  img_item = "./images/{}.png".format( time.strftime("%Y-%m-%d %H-%M-%S", time.gmtime(time.time())) )
                  roi_color = frame[top:bottom, left:right]
                  cv2.imwrite(img_item, roi_color)
                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                cv2.putText(frame, name , (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            out.write(frame)
            cv2.imshow('moving object frame',frame)
            if time.time() - start_timer > 5 and len(face_locations) == 0:
                motion_capture = True
                out.release()

    # assign the current frame as the prev_frame for next one.
    prev_frame = frame

    k = cv2.waitKey(60) & 0xff
    if k == 27:
        break

cv2.destroyAllWindows()
cap.release()
out.release()
