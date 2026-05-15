import random

Music_Lib = [
    "https://www.youtube.com/watch?v=l4uR5QzZ5g4",
    "https://www.youtube.com/watch?v=l4uR5QzZ5g4",
    "https://www.youtube.com/watch?v=l4uR5QzZ5g4",
    "https://www.youtube.com/watch?v=l4uR5QzZ5g4",
    "https://www.youtube.com/watch?v=l4uR5QzZ5g4",
]

def filter_music_links():
    return random.choice(Music_Lib) if Music_Lib else None

Movies_Lib = [
    "https://www.youtube.com/watch?v=l4uR5QzZ5g4",
    "https://www.youtube.com/watch?v=l4uR5QzZ5g4",
    "https://www.youtube.com/watch?v=l4uR5QzZ5g4",
    "https://www.youtube.com/watch?v=l4uR5QzZ5g4",
    "https://www.youtube.com/watch?v=l4uR5QzZ5g4",
]

def filter_movie_links():
    return random.choice(Movies_Lib) if Movies_Lib else None
