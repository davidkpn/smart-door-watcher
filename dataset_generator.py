import face_recognition
import glob

known_face_names = []
known_face_encodings = []

for f in glob.glob(".\\data\\*"):
    name = f.split("\\")[2].split(".")[0]
    image = face_recognition.load_image_file(f)
    face_encoding = face_recognition.face_encodings(image)[0]
    known_face_names.append(name)
    known_face_encodings.append(face_encoding)
