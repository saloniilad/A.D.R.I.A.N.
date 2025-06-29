from flask import Flask, render_template, request, jsonify
import datetime
import random
import re
import json
import urllib.request
import urllib.parse
from html import unescape

app = Flask(__name__)

# Predefined responses and data
JOKES = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "Why did the scarecrow win an award? He was outstanding in his field!",
    "What do you call a fake noodle? An impasta!",
    "Why don't eggs tell jokes? They'd crack each other up!",
    "What do you call a bear with no teeth? A gummy bear!",
    "Why did the math book look so sad? Because it had too many problems!",
    "What do you call a sleeping bull? A bulldozer!",
    "Why don't skeletons fight each other? They don't have the guts!",
    "What do you call a fish wearing a bowtie? Sofishticated!",
    "Why did the coffee file a police report? It got mugged!"
]

FACTS = [
    "The human brain contains approximately 86 billion neurons.",
    "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old.",
    "A group of flamingos is called a 'flamboyance'.",
    "The shortest war in history lasted only 38-45 minutes.",
    "Bananas are berries, but strawberries aren't.",
    "Octopuses have three hearts and blue blood.",
    "A single cloud can weigh more than a million pounds.",
    "Sharks have been around longer than trees.",
    "The Great Wall of China isn't visible from space with the naked eye.",
    "Butterflies taste with their feet."
]

QUOTES = [
    "The only way to do great work is to love what you do. - Steve Jobs",
    "Innovation distinguishes between a leader and a follower. - Steve Jobs",
    "Life is what happens to you while you're busy making other plans. - John Lennon",
    "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
    "It is during our darkest moments that we must focus to see the light. - Aristotle",
    "The only impossible journey is the one you never begin. - Tony Robbins",
    "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
    "The way to get started is to quit talking and begin doing. - Walt Disney",
    "Don't let yesterday take up too much of today. - Will Rogers",
    "You learn more from failure than from success. Don't let it stop you. Failure builds character. - Unknown"
]

RIDDLES = [
    {
        "question": "What has keys but no locks, space but no room, and you can enter but not go inside?",
        "answer": "A keyboard"
    },
    {
        "question": "What gets wet while drying?",
        "answer": "A towel"
    },
    {
        "question": "What has hands but cannot clap?",
        "answer": "A clock"
    },
    {
        "question": "What can travel around the world while staying in a corner?",
        "answer": "A stamp"
    },
    {
        "question": "What has a head, a tail, is brown, and has no legs?",
        "answer": "A penny"
    },
    {
        "question": "What gets bigger the more you take away from it?",
        "answer": "A hole"
    },
    {
        "question": "What has many teeth but cannot bite?",
        "answer": "A zipper"
    },
    {
        "question": "What goes up but never comes down?",
        "answer": "Your age"
    }
]

HOROSCOPE_DATA = {
    "aries": {
        "dates": "March 21 - April 19",
        "element": "Fire",
        "predictions": [
            "Today brings new opportunities for leadership. Trust your instincts and take charge!",
            "Your energy is contagious today. Use it to inspire others around you.",
            "A bold decision you make today will pay off in the long run.",
            "Your competitive spirit will help you overcome any challenges today.",
            "Focus on new beginnings - it's a perfect day to start something fresh."
        ]
    },
    "taurus": {
        "dates": "April 20 - May 20",
        "element": "Earth",
        "predictions": [
            "Stability and patience will be your greatest assets today.",
            "Focus on practical matters and long-term planning today.",
            "Your determination will help you achieve your goals steadily.",
            "Take time to appreciate the simple pleasures in life today.",
            "Trust in your ability to create lasting value in everything you do."
        ]
    },
    "gemini": {
        "dates": "May 21 - June 20",
        "element": "Air",
        "predictions": [
            "Communication is key today. Express your ideas clearly and confidently.",
            "Your curiosity will lead you to interesting discoveries today.",
            "Embrace change and adaptability - they're your superpowers today.",
            "Connect with others through meaningful conversations.",
            "Your quick thinking will help you solve problems creatively."
        ]
    },
    "cancer": {
        "dates": "June 21 - July 22",
        "element": "Water",
        "predictions": [
            "Trust your intuition today - it's especially strong right now.",
            "Focus on nurturing relationships with family and close friends.",
            "Your emotional intelligence will guide you to the right decisions.",
            "Create a comfortable and secure environment for yourself today.",
            "Your caring nature will be appreciated by those around you."
        ]
    },
    "leo": {
        "dates": "July 23 - August 22",
        "element": "Fire",
        "predictions": [
            "Your natural charisma shines brightly today. Use it wisely!",
            "Creative projects will flourish under your passionate energy.",
            "Take center stage - you're meant to be noticed today.",
            "Your generous spirit will bring joy to others around you.",
            "Confidence is your key to success in all endeavors today."
        ]
    },
    "virgo": {
        "dates": "August 23 - September 22",
        "element": "Earth",
        "predictions": [
            "Attention to detail will set you apart from others today.",
            "Your analytical skills will help solve complex problems.",
            "Focus on organization and efficiency in all your tasks.",
            "Your helpful nature will be recognized and appreciated.",
            "Perfectionism serves you well, but don't forget to be kind to yourself."
        ]
    },
    "libra": {
        "dates": "September 23 - October 22",
        "element": "Air",
        "predictions": [
            "Seek balance and harmony in all your relationships today.",
            "Your diplomatic skills will help resolve conflicts peacefully.",
            "Beauty and aesthetics play an important role in your day.",
            "Collaboration will bring better results than working alone.",
            "Your sense of justice guides you toward fair decisions."
        ]
    },
    "scorpio": {
        "dates": "October 23 - November 21",
        "element": "Water",
        "predictions": [
            "Your intensity and passion will drive you toward success today.",
            "Trust your instincts - they're particularly sharp right now.",
            "Transformation and renewal are themes for you today.",
            "Your mysterious nature intrigues and attracts others.",
            "Deep conversations will reveal important insights."
        ]
    },
    "sagittarius": {
        "dates": "November 22 - December 21",
        "element": "Fire",
        "predictions": [
            "Adventure and exploration call to you today. Answer the call!",
            "Your optimistic outlook inspires everyone around you.",
            "Learning something new will bring unexpected benefits.",
            "Your philosophical nature helps others see the bigger picture.",
            "Freedom and independence are essential for your happiness today."
        ]
    },
    "capricorn": {
        "dates": "December 22 - January 19",
        "element": "Earth",
        "predictions": [
            "Your disciplined approach will lead to significant achievements.",
            "Focus on long-term goals and steady progress today.",
            "Your leadership abilities are recognized by others.",
            "Practical solutions work better than complicated ones today.",
            "Your ambition and hard work are about to pay off."
        ]
    },
    "aquarius": {
        "dates": "January 20 - February 18",
        "element": "Air",
        "predictions": [
            "Your innovative ideas will capture everyone's attention today.",
            "Embrace your uniqueness - it's your greatest strength.",
            "Technology and progress feature prominently in your day.",
            "Your humanitarian spirit motivates you to help others.",
            "Think outside the box for creative solutions."
        ]
    },
    "pisces": {
        "dates": "February 19 - March 20",
        "element": "Water",
        "predictions": [
            "Your intuition and empathy guide you to help others today.",
            "Creative and artistic pursuits bring you joy and fulfillment.",
            "Your compassionate nature makes you a trusted confidant.",
            "Dreams and imagination play an important role today.",
            "Trust your feelings - they're leading you in the right direction."
        ]
    }
}

WEATHER_RESPONSES = [
    "🌞 It's a beautiful sunny day with clear skies! Perfect weather for outdoor activities.",
    "🌤️ Partly cloudy with pleasant temperatures. A great day to be outside!",
    "🌧️ Light rain is expected today. Don't forget your umbrella!",
    "⛅ Overcast skies with mild temperatures. Good weather for indoor activities.",
    "🌈 After the rain comes the rainbow! Expect clearing skies later today.",
    "❄️ It's quite chilly today. Bundle up and stay warm!",
    "🌪️ Windy conditions today. Hold onto your hat!",
    "🌅 A perfect day with gentle breeze and comfortable temperatures."
]

def search_wikipedia(query):
    """Search Wikipedia and return a summary of the topic"""
    try:
        query = query.strip()
        if not query:
            return "Please specify what you'd like to search for on Wikipedia."
        
        encoded_query = urllib.parse.quote(query)
        api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_query}"
        
        req = urllib.request.Request(api_url)
        req.add_header('User-Agent', 'JarvisAssistant/1.0')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            
            if 'extract' in data and data['extract']:
                title = data.get('title', query)
                extract = data['extract']
                page_url = data.get('content_urls', {}).get('desktop', {}).get('page', '')
                
                response_text = f"**{title}**\n\n{extract}"
                if page_url:
                    response_text += f"\n\n🔗 Read more: {page_url}"
                
                return response_text
            else:
                return f"I couldn't find detailed information about '{query}' on Wikipedia. Try rephrasing your search or check the spelling."
                
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return f"I couldn't find a Wikipedia page for '{query}'. Try rephrasing your search or check the spelling."
        else:
            return f"There was an error accessing Wikipedia (HTTP {e.code}). Please try again later."
    except urllib.error.URLError:
        return "I'm having trouble connecting to Wikipedia right now. Please check your internet connection and try again."
    except json.JSONDecodeError:
        return "I received an invalid response from Wikipedia. Please try again."
    except Exception as e:
        return f"An unexpected error occurred while searching Wikipedia: {str(e)}"

def get_horoscope(sign):
    """Get horoscope for a zodiac sign"""
    sign = sign.lower().strip()
    if sign in HOROSCOPE_DATA:
        data = HOROSCOPE_DATA[sign]
        prediction = random.choice(data["predictions"])
        return f"🔮 **{sign.capitalize()} Horoscope** ({data['dates']})\n\n**Element:** {data['element']}\n\n**Today's Prediction:** {prediction}\n\n✨ Remember, you create your own destiny!"
    else:
        available_signs = ", ".join(HOROSCOPE_DATA.keys())
        return f"I don't recognize that zodiac sign. Available signs are: {available_signs}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_command', methods=['POST'])
def process_command():
    user_input = request.json.get('command', '').lower()
    response = generate_response(user_input)
    return jsonify({'response': response})

def generate_response(command):
    command = command.lower().strip()
    original_command = command
    
    # Time-related queries
    if any(word in command for word in ['time', 'clock', 'hour']):
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        return f"🕐 The current time is **{current_time}**."
    
    # Date-related queries
    if any(word in command for word in ['date', 'today', 'day']):
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        current_day = datetime.datetime.now().strftime("%A")
        return f"📅 Today is **{current_day}, {current_date}**."
    
    # Horoscope queries
    if any(word in command for word in ['horoscope', 'zodiac', 'astrology', 'sign']):
        # Extract zodiac sign from command
        zodiac_signs = list(HOROSCOPE_DATA.keys())
        found_sign = None
        for sign in zodiac_signs:
            if sign in command:
                found_sign = sign
                break
        
        if found_sign:
            return get_horoscope(found_sign)
        else:
            return "🔮 Please specify your zodiac sign! For example, say 'horoscope aries' or 'my sign is leo'. Available signs: Aries, Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpio, Sagittarius, Capricorn, Aquarius, Pisces."
    
    # Weather queries (simulated)
    if 'weather' in command:
        weather = random.choice(WEATHER_RESPONSES)
        return f"{weather}\n\n*Note: This is a simulated weather report. For real weather data, please check your local weather service.*"
    
    # Quote requests
    if any(word in command for word in ['quote', 'inspiration', 'motivate', 'inspire']):
        quote = random.choice(QUOTES)
        return f"💭 **Inspirational Quote:**\n\n*\"{quote}\"*\n\nHope this inspires you today! ✨"
    
    # Riddle requests
    if any(word in command for word in ['riddle', 'puzzle', 'brain teaser']):
        riddle = random.choice(RIDDLES)
        return f"🧩 **Here's a riddle for you:**\n\n*{riddle['question']}*\n\n🤔 Think you know the answer? Ask me for the solution by saying 'riddle answer' or just tell me what you think!"
    
    # Riddle answer
    if 'riddle answer' in command or 'answer to riddle' in command:
        riddle = random.choice(RIDDLES)  # In a real app, you'd store the current riddle
        return f"💡 **Answer:** {riddle['answer']}\n\nWant another riddle? Just ask! 🧩"
    
    # Calculator
    if any(word in command for word in ['calculate', 'math', 'plus', 'minus', 'multiply', 'divide']):
        try:
            numbers = re.findall(r'\d+\.?\d*', command)
            if len(numbers) >= 2:
                if 'plus' in command or '+' in command:
                    result = float(numbers[0]) + float(numbers[1])
                elif 'minus' in command or '-' in command:
                    result = float(numbers[0]) - float(numbers[1])
                elif 'multiply' in command or '*' in command or 'times' in command:
                    result = float(numbers[0]) * float(numbers[1])
                elif 'divide' in command or '/' in command:
                    if float(numbers[1]) == 0:
                        return "🚫 I can't divide by zero! That would break the universe! 🌌"
                    result = float(numbers[0]) / float(numbers[1])
                else:
                    return "🧮 I can help you with basic math operations. Try saying 'calculate 5 plus 3'."
                
                if result == int(result):
                    return f"🧮 **Calculation Result:** {int(result)}"
                else:
                    return f"🧮 **Calculation Result:** {result:.2f}"
        except:
            return "🧮 I couldn't process that calculation. Try saying something like 'calculate 10 plus 5'."
    
    # Wikipedia searches
    wikipedia_triggers = ['wikipedia', 'wiki', 'tell me about', 'information about', 'what is', 'who is', 'info about']
    if any(trigger in command for trigger in wikipedia_triggers):
        search_term = command
        
        for trigger in wikipedia_triggers:
            search_term = search_term.replace(trigger, '').strip()
        
        question_words = ['give me', 'can you', 'please', 'information', 'info', 'about', 'on']
        for word in question_words:
            search_term = search_term.replace(word, '').strip()
        
        search_term = ' '.join(search_term.split())
        
        if search_term:
            return search_wikipedia(search_term)
        else:
            return "📚 What would you like me to search for on Wikipedia? Try saying 'tell me about Harry Potter' or 'Wikipedia artificial intelligence'."
    
    # Jokes
    if any(word in command for word in ['joke', 'funny', 'laugh', 'humor']):
        joke = random.choice(JOKES)
        return f"😂 **Here's a joke for you:**\n\n{joke}\n\nHope that made you smile! 😄"
    
    # Facts
    if any(word in command for word in ['fact', 'tell me something', 'interesting', 'trivia']):
        fact = random.choice(FACTS)
        return f"🧠 **Interesting Fact:**\n\n{fact}\n\nPretty cool, right? 🤓"
    
    # Coin flip
    if any(phrase in command for phrase in ['flip a coin', 'coin flip', 'heads or tails']):
        result = random.choice(['Heads', 'Tails'])
        return f"🪙 **Coin Flip Result:** {result}!\n\nWant to flip again? Just ask! 🎲"
    
    # Dice roll
    if any(phrase in command for phrase in ['roll a dice', 'roll dice', 'dice roll']):
        result = random.randint(1, 6)
        return f"🎲 **Dice Roll Result:** {result}!\n\nFeeling lucky? Roll again! 🍀"
    
    # Random number
    if 'random number' in command:
        numbers = re.findall(r'\d+', command)
        if len(numbers) >= 2:
            min_num, max_num = int(numbers[0]), int(numbers[1])
            if min_num > max_num:
                min_num, max_num = max_num, min_num
            result = random.randint(min_num, max_num)
            return f"🎯 **Random Number ({min_num}-{max_num}):** {result}"
        else:
            result = random.randint(1, 100)
            return f"🎯 **Random Number (1-100):** {result}"
    
    # Password generator
    if any(word in command for word in ['password', 'generate password']):
        import string
        length = 12
        numbers = re.findall(r'\d+', command)
        if numbers:
            length = min(int(numbers[0]), 50)  # Max 50 characters
        
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(random.choice(characters) for _ in range(length))
        return f"🔐 **Generated Password ({length} characters):**\n\n`{password}`\n\n⚠️ Make sure to store this securely!"
    
    # Color generator
    if any(word in command for word in ['color', 'colour', 'hex color']):
        color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        return f"🎨 **Random Color:** {color}\n\nThis would look great in your next design! ✨"
    
    # Opening websites
    if 'open' in command:
        if 'google' in command:
            return "🌐 Opening Google for you!"
        elif 'youtube' in command:
            return "📺 Opening YouTube for you!"
        elif 'github' in command:
            return "💻 Opening GitHub for you!"
        elif 'stackoverflow' in command:
            return "💡 Opening Stack Overflow for you!"
        elif 'reddit' in command:
            return "🤖 Opening Reddit for you!"
        elif 'twitter' in command:
            return "🐦 Opening Twitter for you!"
        elif 'facebook' in command:
            return "📘 Opening Facebook for you!"
        elif 'instagram' in command:
            return "📸 Opening Instagram for you!"
        elif 'linkedin' in command:
            return "💼 Opening LinkedIn for you!"
        else:
            return "🌐 I can help you open Google, YouTube, GitHub, Stack Overflow, Reddit, Twitter, Facebook, Instagram, LinkedIn, or other websites. Just specify which one!"
    
    # Clear chat
    if any(word in command for word in ['clear', 'reset', 'clean']):
        return "🧹 Chat cleared! How can I help you now?"
    
    # Greetings
    if any(word in command for word in ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']):
        greetings = [
            "👋 Hello! I'm Adrian, your personal assistant. How can I help you today?",
            "🤖 Hi there! I'm ready to assist you with various tasks. What would you like to do?",
            "✨ Greetings! I'm Adrian. What can I do for you today?",
            "😊 Hey! Great to see you. How can I assist you right now?"
        ]
        return random.choice(greetings)
    
    # Help
    if any(word in command for word in ['help', 'what can you do', 'commands', 'capabilities']):
        return """🚀 **I can help you with many things! Here are my capabilities:**

🕐 **Time & Date** - "What time is it?" or "What's today's date?"
🧮 **Calculator** - "Calculate 25 plus 75" or "What's 12 times 8?"
📚 **Wikipedia** - "Tell me about Harry Potter" or "Wikipedia artificial intelligence"
🔮 **Horoscope** - "Horoscope Leo" or "My sign is Aries"
🌤️ **Weather** - "What's the weather like?" (simulated)
💭 **Quotes** - "Give me an inspirational quote"
🧩 **Riddles** - "Tell me a riddle" or "Give me a brain teaser"
🌐 **Open Websites** - "Open Google", "Open YouTube", etc.
😂 **Entertainment** - Jokes, facts, coin flip, dice roll
🎯 **Random Generators** - Numbers, passwords, colors
🧹 **Clear Chat** - "Clear" to reset our conversation

Just talk to me naturally! I understand many different ways of asking for the same thing. ✨"""
    
    # Goodbye
    if any(word in command for word in ['bye', 'goodbye', 'see you', 'exit', 'quit']):
        farewells = [
            "👋 Goodbye! It was nice chatting with you. Feel free to come back anytime!",
            "🤖 See you later! I'll be here whenever you need assistance.",
            "✨ Farewell! Thanks for using me. Have a great day!",
            "😊 Until next time! I'm always here to help. Take care!"
        ]
        return random.choice(farewells)
    
    # Ping (for connection testing)
    if command.strip() == 'ping':
        return "🏓 Pong! I'm online and ready to help."
    
    # Default response with suggestions
    default_responses = [
        "🤔 I'm not sure I understand that. Could you please rephrase your question? Try asking me about time, calculations, horoscopes, Wikipedia topics, or say 'help' to see what I can do.",
        "💭 That's interesting! Can you tell me more about what you're looking for? I can help with time, math, horoscopes, Wikipedia searches, opening websites, and much more!",
        "🧠 I'm still learning. Try asking me about the time, calculations, your horoscope, jokes, Wikipedia topics, or say 'help' to see my full capabilities.",
        "🎯 Hmm, I didn't catch that. Try asking me something like 'What time is it?', 'Tell me about Python programming', 'Horoscope Gemini', or 'Calculate 15 times 4'."
    ]
    return random.choice(default_responses)

if __name__ == '__main__':
    app.run(debug=True, port=5000)