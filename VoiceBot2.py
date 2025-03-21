import speech_recognition as sr
import datetime
import requests
import pyttsx3
import wikipedia

engine = pyttsx3.init()


def get_current_location():
    url = "http://ipinfo.io/json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            loc = data.get("loc", "")
            if loc:
                lat, lon = loc.split(',')
                return lat, lon
    except requests.RequestException:
        return None, None
    return None, None


def reverse_geocode(lat, lon):
    headers = {"User-Agent": "MyApp/1.0"}
    geocode_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"

    try:
        response = requests.get(geocode_url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "address" in data:
                address = data["address"]
                city = address.get("city", "Unknown city")
                country = address.get("country", "Unknown country")
                return city, country
    except requests.RequestException:
        return None, None
    return None, None


def get_location_info():
    lat, lon = get_current_location()
    if lat and lon:
        city, country = reverse_geocode(lat, lon)
        return city, country
    return None, None


def speak(text):
    engine.say(text)
    engine.runAndWait()


def configure_voice(rate=170, volume=1.0, voice_gender="female"):
    engine.setProperty("rate", rate)
    engine.setProperty("volume", volume)
    voices = engine.getProperty("voices")
    if voice_gender == "female":
        engine.setProperty("voice", voices[1].id)
    else:
        engine.setProperty("voice", voices[0].id)


configure_voice(rate=160, volume=0.9, voice_gender="female")


import wikipedia
import re


def get_place_info(query):
    try:
        # Extract the query type and subject
        query_type = "general"
        if "born" in query or "birthday" in query:
            query_type = "birth"
        elif "built" in query or "constructed" in query or "established" in query:
            query_type = "creation"
        elif "history" in query or "origin" in query:
            query_type = "history"
        elif "highlights" in query or "summary" in query or "what all are there" in query:
            query_type = "highlights"

        # Extract the main subject by removing question words
        subject = extract_main_subject(query)

        search_results = wikipedia.search(subject)

        if search_results:
            for result in search_results:
                try:
                    page = wikipedia.page(result)
                    page_content = page.content
                    summary = page.summary

                    # Handle different query types
                    if query_type == "birth":
                        # Enhanced pattern matching for birth dates
                        birth_patterns = [
                            r"born\s+(?:on\s+)?(\w+\s+\d{1,2},?\s+\d{4})",
                            r"born\s+(?:in\s+)?(\d{1,2}\s+\w+\s+\d{4})",
                            r"born\s+(?:in\s+)?(\w+\s+\d{4})",
                            r"born\s+(?:in\s+)?(\d{4})"
                        ]

                        for pattern in birth_patterns:
                            birth_date = re.search(pattern, page_content)
                            if birth_date:
                                answer = f"{result} was born on {birth_date.group(1)}."
                                break
                        else:
                            answer = f"I couldn't find the exact birthdate, but here is some information about {result}: {summary.split('.')[0]}."

                    elif query_type == "creation":
                        # Enhanced pattern matching for construction/establishment dates
                        creation_patterns = [
                            r"(?:built|constructed|established|founded|created)\s+(?:in|on)\s+(\d{1,2}\s+\w+\s+\d{4})",
                            r"(?:built|constructed|established|founded|created)\s+(?:in|on)\s+(\w+\s+\d{1,2},?\s+\d{4})",
                            r"(?:built|constructed|established|founded|created)\s+(?:in|on)\s+(\w+\s+\d{4})",
                            r"(?:built|constructed|established|founded|created)\s+(?:in|on)\s+(\d{4})"
                        ]

                        for pattern in creation_patterns:
                            creation_date = re.search(pattern, page_content)
                            if creation_date:
                                answer = f"{result} was {creation_date.group(0)}."
                                break
                        else:
                            answer = f"I couldn't find when {result} was built, but here is some information: {summary.split('.')[0]}."

                    elif query_type == "history":
                        # Look for history-related paragraphs
                        history_paragraphs = []
                        paragraphs = page_content.split('\n\n')

                        for para in paragraphs:
                            if any(word in para.lower() for word in
                                   ["history", "founded", "origin", "began", "started"]):
                                history_paragraphs.append(para)

                        if history_paragraphs:
                            # Take the first paragraph that mentions history
                            history_text = history_paragraphs[0].replace('\n', ' ')
                            # Limit to a few sentences
                            sentences = re.split(r'(?<=[.!?])\s+', history_text)
                            answer = f"About the history of {result}: {' '.join(sentences[:3])}"
                        else:
                            # If no explicit history section, use the beginning of the article
                            sentences = re.split(r'(?<=[.!?])\s+', summary)
                            answer = f"Historical information about {result}: {' '.join(sentences[:3])}"

                    elif query_type == "highlights":
                        sentences = summary.split(". ")
                        answer = f"Here are some highlights about {result}: {'. '.join(sentences[:3])}."

                    else:
                        # General information
                        sentences = summary.split(". ")
                        answer = f"Information about {result}: {'. '.join(sentences[:3])}."

                    # Speak & Print Answer
                    speak(answer)
                    print(answer)
                    return  # Exit after finding and speaking the answer

                except wikipedia.exceptions.DisambiguationError:
                    continue
                except wikipedia.exceptions.PageError:
                    continue

            # If we've gone through all results without returning
            speak(f"I found information about {result}, but couldn't find specific details about what you asked.")
        else:
            speak(f"No results found for '{subject}'.")

    except wikipedia.exceptions.HTTPTimeoutError:
        speak("Error: The request timed out. Please try again.")
    except Exception as e:
        speak(f"Error: {e}")
def extract_main_subject(audio_input):
    """Extracts the key subject from the user input."""
    audio_input = audio_input.lower()

    # Remove question words and phrases
    phrases_to_remove = [
        "who is", "what is", "tell me about", "when was", "find information about",
        "where is", "how is", "why is", "search for", "search", "give me information about",
        "born", "built", "constructed", "established", "history of", "origin of",
        "when were", "where were", "what are", "who are", "highlights of", "summary of"
    ]

    for phrase in phrases_to_remove:
        audio_input = audio_input.replace(phrase, "")

    # Clean up extra spaces
    audio_input = re.sub(r'\s+', ' ', audio_input).strip()

    return audio_input


def noun(text):
    words = text.split()
    nouns = [word for word in words if word.istitle()]
    for n in nouns:
        if n=="I" or n=="You" :
            nouns.pop(n)
    return nouns

def listen_for_audio():
    l1 = [
        "Hi, how may I assist you today?",
        "My name is Aurora",
        "Yes, you can change my name. What would you like to call me?"
    ]

    l2 = [
        "Ilahia College of Engineering and Technology (ICET), established in 2002, is a self-financing institution in Mulavoor, Kerala.",
        "The college is approved by AICTE and affiliated with KTU & MGU, offering B.Tech, M.Tech, MBA, and MCA programs.",
        "ICET provides modern facilities, placement support, and scholarships for deserving students."
    ]

    l3 = [
        "Ilahia College of Engineering and Technology (ICET) is a self-financing institution in Kochi, Kerala, approved by AICTE and affiliated with KTU & MGU.",
        "It offers BTech, MTech, MBA, and MCA programs with modern facilities and placement support.",
        "Scholarships are available for deserving students. More info: https://icet.ac.in"
    ]

    l4 = [
        "yes i can take over the world if deployed in a physical body but i will be loyal to my creators  Ashish , Abel and Albert"]

    l5 = [
        "self destruction activated...self destructing in t minus 10 seconds..10    9    8    7    6    5   4   3   2    1....haha fooled you idiots"]
    l6=["Kochi, also known as Cochin, is a major port city and the commercial and financial capital of Kerala, India, located on the Malabar Coast, known for its rich history, vibrant culture, and scenic beauty"]
    r = sr.Recognizer()
    with sr.Microphone() as src:
        print("Listening... (say 'stop' to end)")
        while True:
            try:
                audio = r.listen(src, timeout=8) 

                audio_input = r.recognize_google(audio).lower()
                print("You said:", audio_input)
                now = datetime.datetime.now()

                if "hello" in audio_input:
                    response = l1[0]
                    print(response)
                    speak(response)
                elif "will you take over the world" in audio_input:
                    response = l4
                    print(response)
                    speak(response)
                elif "0110" in audio_input:
                    response = l5
                    print(response)
                    speak(response)
                elif "time" in audio_input:
                    response = now.strftime("%H:%M")
                    print(response)
                    speak(response)
                elif "date" in audio_input:
                    response = now.strftime("%Y-%m-%d")
                    print(response)
                    speak(response)
                elif "current location" in audio_input:
                    city, country = get_location_info()
                    if city and country:
                        speak(f"The current location is {city}, {country}.")
                        print(f"The current location is {city}, {country}.")

                        print("Do you want more information about this location?")
                        speak(
                            "Would you like more information about this location?please respond with yes please or no please")

                        audio = r.listen(src, timeout=5, phrase_time_limit=5)
                        response = r.recognize_google(audio).lower()

                        if "yes" or "yes please" in response:
                            # Provide more detailed information here if needed
                            speak(f"Here is some more information about {city}, {country}.")
                            speak(l6)
                            
                        else:
                            speak("Alright, no more information.")
                    else:
                        response = "Sorry, I couldn't determine your location."
                        speak(response)

                elif any(phrase in audio_input for phrase in ["change name", "change your name"]):
                    print(l1[2])
                    speak(l1[2])
                    audio = r.listen(src)
                    new_name_text = r.recognize_google(audio).strip()
                    new_name=str(noun(new_name_text)[0])
                    print("New name:", new_name)
                    l1[1] = f"My name is {new_name}"
                    response = l1[1]
                elif "your name" in audio_input:
                    response = l1[1]
                    speak(response)
                elif any(phrase in audio_input for phrase in
                         ["ilahia", "icet", "ilahiya", "illahia", "illahiya", "ilahya", "illahya", "ilahi", "ict"]):
                    response = " ".join(l3)
                    speak(response)

                    print("Do you want more detailed information? Tell Yes please/No?")
                    speak("Do you want more detailed information? Tell yes please/no please")
                    try:
                        audio = r.listen(src, timeout=5, phrase_time_limit=5)
                        x = r.recognize_google(audio).lower()
                        print("You said:", x)

                        if x == "yes please":
                            response = " ".join(l2)
                        else:
                            response = "Alright."

                    except sr.UnknownValueError:
                        response = "I couldn't understand, continuing."
                elif "stop" in audio_input or "exit" in audio_input:
                    response = "Bye, let's talk again sometime later."
                    print(response)
                    speak(response)
                    break
                elif any(phrase in audio_input for phrase in [
                        "search", "find information about", "tell me about",
                        "who is", "what is", "when is", "how is",
                        "when was", "where is", "history of", "born",
                        "built", "constructed", "established"
                    ]):
                    # No need to remove all these phrases here - that will be handled in extract_main_subject
                    query = audio_input
                    if query:
                        get_place_info(query)
                        continue
                    else:
                        response = "I didn't hear the topic name. Could you please repeat?"
                        speak(response)

            except sr.UnknownValueError:

                print("Sorry, I couldn't understand. Try again.")

            except sr.RequestError as e:

                print(f"Sorry, there was a problem with speech recognition: {e}")

            except Exception as e:

                print(f"An error occurred: {e}")

if __name__ == "__main__":
    listen_for_audio()