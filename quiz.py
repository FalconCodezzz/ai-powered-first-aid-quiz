import pygame
import sys
import random
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv  # <-- NEW: Import the dotenv function

# --- AI and Game Configuration ---
load_dotenv()  # <-- NEW: Load environment variables from the .env file

# Configuration
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800
BACKGROUND_COLOR = (30, 30, 30)
TITLE_COLOR = (255, 215, 0)
TEXT_COLOR = (240, 240, 240)
CORRECT_COLOR = (0, 255, 0)
INCORRECT_COLOR = (255, 0, 0)
BUTTON_COLOR = (70, 70, 70)
BUTTON_HOVER_COLOR = (100, 100, 100)
AI_BUTTON_COLOR = (138, 43, 226)  # Purple for AI features
AI_BUTTON_HOVER_COLOR = (160, 82, 245)
BUTTON_RADIUS = 10

# Font sizes
TITLE_FONT_SIZE = 80
COUNTER_FONT_SIZE = 48
QUESTION_FONT_SIZE = 40
BUTTON_FONT_SIZE = 32
SCORE_FONT_SIZE = 60
MESSAGE_FONT_SIZE = 48
AI_FONT_SIZE = 24

# Layout constants
HOME_BUTTON_WIDTH = 360
HOME_BUTTON_HEIGHT = 100
QUESTION_BUTTON_HEIGHT = 80
BUTTON_PADDING = 15
QUESTION_MAX_WIDTH_PX = WINDOW_WIDTH - 150 

# AI Integration Class
class AIAssistant:
    def __init__(self):
        self.model = None
        self.initialize_model()

    def initialize_model(self):
        """Initialize Gemini model with API key from environment"""
        try:
            # This line now works because load_dotenv() was called earlier
            api_key = os.getenv('GEMINI_API_KEY') 
            if not api_key:
                print("="*60)
                print("WARNING: GEMINI_API_KEY not found in your .env file or environment.")
                print("AI features will be disabled. The game will still work in regular mode.")
                print("To enable AI: Create a .env file with your API key.")
                print("="*60)
                return

            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
            print("AI Assistant initialized successfully.")
        except Exception as e:
            print(f"Failed to initialize AI model: {e}")
            self.model = None
            
    def _parse_json_from_response(self, text):
        """Robustly parse JSON from a string that might contain other text."""
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0]
        
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = text[json_start:json_end]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    print(f"Failed to parse JSON from AI response: {e}")
                    print(f"Raw response part: {json_str}")
                    return None
        return None

    def generate_personalized_question(self, difficulty, user_weak_topics=None):
        """Generate a personalized first-aid question based on user's weak areas"""
        if not self.model:
            return None

        try:
            weak_areas = ", ".join(user_weak_topics) if user_weak_topics else "general first aid"
            prompt = f"""Create a practical, scenario-based first-aid quiz question.
Difficulty level: {difficulty} (1=basic, 2=intermediate, 3=advanced).
Focus on: {weak_areas}.

Format your response as a single, clean JSON object. Do not include any other text or markdown.
The JSON object must be in this exact format:
{{
   "question": "Your question text here.",
   "options": ["Option A", "Option B", "Option C", "Option D"],
   "answer": 0,
   "tip": "A brief, helpful tip related to the correct answer.",
   "difficulty": {difficulty}
}}
"""
            response = self.model.generate_content(prompt)
            return self._parse_json_from_response(response.text)
        except Exception as e:
            print(f"AI question generation failed: {e}")
            return None

    def get_detailed_explanation(self, question, user_answer_idx, correct_answer_idx, options):
        """Get AI-powered detailed explanation for wrong answers"""
        if not self.model:
            return "AI explanation unavailable. Please check your API key setup."

        try:
            user_answer_text = options[user_answer_idx]
            correct_answer_text = options[correct_answer_idx]
            prompt = f"""You are a calm and encouraging first-aid instructor. A student answered a quiz question incorrectly.

Question: "{question}"
Student's incorrect choice: "{user_answer_text}"
The correct answer was: "{correct_answer_text}"

Please provide a clear, educational explanation in 2-3 sentences. Structure your response to:
1. Explain why the student's answer is incorrect or less ideal.
2. Explain why the correct answer is the best course of action.
3. Provide a simple, practical tip to help remember this for the future.

Keep your tone positive and focus on learning."""

            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"AI explanation failed: {e}")
            return "AI explanation unavailable due to an error."

    def generate_study_plan(self, weak_topics, score):
        """Generate a personalized study plan based on performance"""
        if not self.model:
            return "AI study plan unavailable. Please check your API key setup."

        try:
            prompt = f"""Create a concise, personalized first-aid study plan for a student who scored {score}/10 on a quiz.

Their identified weak areas are: {', '.join(weak_topics) if weak_topics else 'General improvement needed'}.

Provide the plan with these sections, using markdown for clarity:
- **Top 3 Priority Topics:** List the three most important topics to study.
- **Practice Activities:** Suggest 2-3 practical, simple activities they can do.
- **Key Concepts to Review:** Mention 2-3 core principles they should focus on.

Keep the tone encouraging and the advice actionable."""
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"AI study plan generation failed: {e}")
            return "AI study plan unavailable due to an error."

# ... (The rest of the code is exactly the same as before) ...
# ... No other changes are needed in the QUESTION_BANK or any of the game classes.

# Question Bank
QUESTION_BANK = [
   # Difficulty 1 - Basic
   {
       "question": "What should you do first when someone is unconscious but breathing normally?",
       "options": ["Give them water", "Check for a pulse", "Place them in the recovery position", "Slap their face to wake them up"],
       "answer": 2, "difficulty": 1, "tip": "The recovery position helps keep their airway open and clear.", "topic": "unconsciousness"
   },
   {
       "question": "What is the first step for treating a minor cut or scrape?",
       "options": ["Apply a sterile dressing", "Wash the area with soap and water", "Apply antibiotic ointment", "Cover it with a large bandage"],
       "answer": 1, "difficulty": 1, "tip": "Cleaning a wound first helps prevent infection.", "topic": "wound care"
   },
   {
       "question": "For an adult nosebleed, what is the correct action?",
       "options": ["Tilt the head back and pinch the bridge of the nose", "Lie down flat", "Pinch the soft part of the nose and lean forward", "Stuff cotton deep into the nostril"],
       "answer": 2, "difficulty": 1, "tip": "Leaning forward prevents blood from going down the throat.", "topic": "bleeding"
   },
   {
       "question": "How should you help someone who is choking but can still cough?",
       "options": ["Hit their back hard", "Encourage them to keep coughing", "Give abdominal thrusts", "Give them water"],
       "answer": 1, "difficulty": 1, "tip": "Coughing is the body's natural way to clear blockages.", "topic": "choking"
   },
   {
       "question": "What should you apply to a minor burn immediately?",
       "options": ["Ice", "Butter", "Cool running water for 10-20 minutes", "Bandage tightly"],
       "answer": 2, "difficulty": 1, "tip": "Cool water stops the burning process and reduces pain.", "topic": "burns"
   },
    # Difficulty 2 - Intermediate
   {
       "question": "A person has chest pain spreading to their arms and is sweating. What should you do first while waiting for an ambulance?",
       "options": ["Give them a sugary drink", "Help them into a comfortable position (e.g., half-sitting)", "Make them walk around to improve circulation", "Give them a paper bag to breathe into"],
       "answer": 1, "difficulty": 2, "tip": "Keeping a potential heart attack victim calm and comfortable reduces strain on the heart. Call 911 immediately.", "topic": "heart attack"
   },
   {
       "question": "How do you control severe bleeding from a limb wound after applying direct pressure doesn't work?",
       "options": ["Wash the wound with water", "Apply a tourniquet above the wound", "Apply more dressings on top of the first", "Remove the soaked dressing and apply a new one"],
       "answer": 2, "difficulty": 2, "tip": "Do not remove the original dressing; add more on top to maintain pressure.", "topic": "bleeding"
   },
   {
       "question": "What is the correct depth for chest compressions on an adult during CPR?",
       "options": ["About 1 inch (2.5 cm)", "At least 2 inches (5 cm)", "About 4 inches (10 cm)", "As deep as you can push"],
       "answer": 1, "difficulty": 2, "tip": "2 inches (5 cm) is the standard depth to effectively circulate blood.", "topic": "CPR"
   },
   {
       "question": "During a seizure, what is a key safety measure you should take for the person?",
       "options": ["Hold them down firmly to stop the shaking", "Put something in their mouth to prevent tongue biting", "Clear the area of hard or sharp objects", "Try to give them water immediately after"],
       "answer": 2, "difficulty": 2, "tip": "Protecting from injury is key. Never restrain them or put anything in their mouth.", "topic": "seizures"
   },
   {
       "question": "What does 'RICE' stand for when treating sprains and strains?",
       "options": ["Run, Ice, Call, Emergency", "Rest, Ice, Compression, Elevation", "Reassure, Inspect, Cover, Evacuate", "Rotate, Isolate, Cool, Examine"],
       "answer": 1, "difficulty": 2, "tip": "RICE is the standard procedure for managing soft tissue injuries.", "topic": "sprains"
   },
    # Difficulty 3 - Advanced
   {
       "question": "A person is pale, cold, clammy, and confused after an injury. They are likely in shock. What should you do?",
       "options": ["Give them a hot drink", "Have them sit up straight", "Lay them down and elevate their legs (if no leg injury)", "Walk them around slowly"],
       "answer": 2, "difficulty": 3, "tip": "Elevating the legs helps blood flow back to vital organs in cases of shock.", "topic": "shock"
   },
   {
       "question": "What does the 'T' in the FAST acronym for stroke recognition stand for?",
       "options": ["Temperature", "Talk", "Time", "Tingling"],
       "answer": 2, "difficulty": 3, "tip": "Time to call emergency services is critical for stroke outcomes. (F-Face, A-Arms, S-Speech, T-Time).", "topic": "stroke"
   },
   {
       "question": "What is the standard ratio of chest compressions to rescue breaths for a single rescuer performing CPR on an adult?",
       "options": ["15 compressions to 2 breaths", "30 compressions to 2 breaths", "5 compressions to 1 breath", "100 compressions with no breaths"],
       "answer": 1, "difficulty": 3, "tip": "30:2 is the universal ratio for adult CPR to balance circulation and oxygenation.", "topic": "CPR"
   },
   {
       "question": "A person is having a severe allergic reaction (anaphylaxis) and has a prescribed epinephrine auto-injector (EpiPen). What should you do?",
       "options": ["Wait to see if they get better on their own", "Help them use the auto-injector and then call 911", "Give them an antihistamine pill and wait", "Lay them flat and give them water"],
       "answer": 1, "difficulty": 3, "tip": "Anaphylaxis is a life-threatening emergency. Use the EpiPen immediately and always call 911.", "topic": "allergic reactions"
   },
   {
       "question": "If you suspect someone has a spinal injury after a fall, what is the most important principle to follow?",
       "options": ["Help them get up and walk to a chair", "Keep their head, neck, and back perfectly still", "Roll them into the recovery position immediately", "Give them a pillow to make them comfortable"],
       "answer": 1, "difficulty": 3, "tip": "Preventing movement is crucial to avoid causing further damage to the spinal cord.", "topic": "spinal injuries"
   }
]

def wrap_text(text, font, max_pixel_width):
    """Wrap text to fit within a specific pixel width."""
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        # Test if adding the new word exceeds the width
        test_line = current_line + " " + word if current_line else word
        test_width, _ = font.size(test_line)
        if test_width <= max_pixel_width:
            current_line = test_line
        else:
            # If the current line is not empty, add it to the list
            if current_line:
                lines.append(current_line)
            # Start a new line with the current word
            current_line = word
    # Append the last line
    if current_line:
        lines.append(current_line)
    return lines

def draw_rounded_rect(surface, color, rect, radius):
    """Draw a rectangle with rounded corners"""
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def draw_text_centered(surface, text, font, color, y_pos, max_width=None):
    """Draw text centered horizontally, with optional wrapping."""
    if max_width:
        lines = wrap_text(text, font, max_width)
        line_height = font.get_height()
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, color)
            x_pos = (WINDOW_WIDTH - text_surface.get_width()) // 2
            surface.blit(text_surface, (x_pos, y_pos + i * line_height))
    else:
        text_surface = font.render(text, True, color)
        x_pos = (WINDOW_WIDTH - text_surface.get_width()) // 2
        surface.blit(text_surface, (x_pos, y_pos))

def draw_multiline_text(surface, lines, font, color, x, y, line_height, centered=False):
   """Draw multiple lines of text, with optional horizontal centering."""
   for i, line in enumerate(lines):
       text_surface = font.render(line, True, color)
       draw_x = x
       if centered:
           draw_x = (WINDOW_WIDTH - text_surface.get_width()) // 2
       surface.blit(text_surface, (draw_x, y + i * line_height))

class Button:
    def __init__(self, x, y, width, height, text, font, is_ai_button=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.is_hovered = False
        self.is_ai_button = is_ai_button

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        elif event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        return False

    def draw(self, surface):
        if self.is_ai_button:
            color = AI_BUTTON_HOVER_COLOR if self.is_hovered else AI_BUTTON_COLOR
        else:
            color = BUTTON_HOVER_COLOR if self.is_hovered else BUTTON_COLOR

        draw_rounded_rect(surface, color, self.rect, BUTTON_RADIUS)

        # Use the corrected wrap_text function for button text
        text_lines = wrap_text(self.text, self.font, self.rect.width * 0.9)
        line_height = self.font.get_height()
        total_height = len(text_lines) * line_height
        start_y = self.rect.centery - total_height // 2

        for i, line in enumerate(text_lines):
            text_surface = self.font.render(line, True, TEXT_COLOR)
            text_x = self.rect.centerx - text_surface.get_width() // 2
            text_y = start_y + i * line_height
            surface.blit(text_surface, (text_x, text_y))

class QuizGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("AI-Powered First-Aid Quiz")
        self.clock = pygame.time.Clock()

        # Initialize fonts
        self.title_font = pygame.font.Font(None, TITLE_FONT_SIZE)
        self.counter_font = pygame.font.Font(None, COUNTER_FONT_SIZE)
        self.question_font = pygame.font.Font(None, QUESTION_FONT_SIZE)
        self.button_font = pygame.font.Font(None, BUTTON_FONT_SIZE)
        self.score_font = pygame.font.Font(None, SCORE_FONT_SIZE)
        self.message_font = pygame.font.Font(None, MESSAGE_FONT_SIZE)
        self.ai_font = pygame.font.Font(None, AI_FONT_SIZE)

        # AI Assistant
        self.ai_assistant = AIAssistant()

        # Game state
        self.state = "home"
        self.current_difficulty = 1
        self.questions = []
        self.index = -1
        self.score = 0
        self.total_questions_in_round = 10
        self.feedback_text = ""
        self.feedback_color = TEXT_COLOR
        self.wrong_topics = []
        self.ai_explanation = ""
        self.study_plan = ""
        self.last_user_answer = -1

        # UI elements
        self.start_button = Button((WINDOW_WIDTH - HOME_BUTTON_WIDTH) // 2, 300, HOME_BUTTON_WIDTH, HOME_BUTTON_HEIGHT, "Start Quiz", self.button_font)
        self.ai_mode_button = Button((WINDOW_WIDTH - HOME_BUTTON_WIDTH) // 2, 420, HOME_BUTTON_WIDTH, HOME_BUTTON_HEIGHT, "AI Adaptive Mode", self.button_font, is_ai_button=True)
        self.retake_button = Button((WINDOW_WIDTH - HOME_BUTTON_WIDTH) // 2, 460, HOME_BUTTON_WIDTH, HOME_BUTTON_HEIGHT, "Retake Quiz", self.button_font)
        self.ai_explanation_button = Button(50, WINDOW_HEIGHT - 120, 250, 60, "Get AI Explanation", self.ai_font, is_ai_button=True)
        self.continue_button = Button(WINDOW_WIDTH - 250, WINDOW_HEIGHT - 120, 200, 60, "Continue", self.button_font)
        self.study_plan_button = Button((WINDOW_WIDTH - HOME_BUTTON_WIDTH) // 2, 580, HOME_BUTTON_WIDTH, HOME_BUTTON_HEIGHT, "Get AI Study Plan", self.button_font, is_ai_button=True)
        
        self.option_buttons = []
        self.ai_mode = False

    def get_questions_by_difficulty(self, difficulty, exclude_list=[]):
        """Get questions matching difficulty, excluding those already used."""
        return [q for q in QUESTION_BANK if q['difficulty'] == difficulty and q not in exclude_list]

    def adjust_difficulty(self):
        """Adjust difficulty based on performance in the last 3 questions."""
        if len(self.questions) > 3:
             # Look at the last 3 answers
            recent_answers = [q['correct'] for q in self.questions[-3:] if 'correct' in q]
            if len(recent_answers) == 3:
                performance = sum(recent_answers) / 3
                if performance > 0.7 and self.current_difficulty < 3:
                    self.current_difficulty += 1
                    print(f"Difficulty increased to {self.current_difficulty}")
                elif performance < 0.4 and self.current_difficulty > 1:
                    self.current_difficulty -= 1
                    print(f"Difficulty decreased to {self.current_difficulty}")

    def start_quiz(self, ai_mode=False):
        """Start or restart the quiz"""
        self.ai_mode = ai_mode and self.ai_assistant.model is not None
        self.questions = []
        self.current_difficulty = 1 # Reset difficulty
        weak_topics = list(set(self.wrong_topics)) if self.wrong_topics else None

        if self.ai_mode:
            print("Starting AI Adaptive Mode...")
            # Generate 5 AI questions + 5 from bank
            num_ai_questions = 5
            for _ in range(num_ai_questions):
                ai_question = self.ai_assistant.generate_personalized_question(self.current_difficulty, weak_topics)
                if ai_question and 'question' in ai_question:
                    ai_question['topic'] = 'ai_generated'
                    self.questions.append(ai_question)
                else:
                    print("AI question generation failed. Using a fallback question from bank.")
                    fallback_pool = [q for q in QUESTION_BANK if q not in self.questions]
                    if fallback_pool:
                        self.questions.append(random.choice(fallback_pool))
        
        # Fill remaining with regular questions from the bank
        needed = self.total_questions_in_round - len(self.questions)
        bank_pool = [q for q in QUESTION_BANK if q not in self.questions]
        if len(bank_pool) < needed:
             self.questions.extend(bank_pool)
        else:
             self.questions.extend(random.sample(bank_pool, needed))

        random.shuffle(self.questions)
        self.index = -1
        self.score = 0
        self.wrong_topics = []
        self.next_question()

    def next_question(self):
        self.index += 1
        if self.index >= len(self.questions):
            self.state = "summary"
            return

        self.state = "question"
        current_q = self.questions[self.index]
        self.option_buttons = []
        button_width = (WINDOW_WIDTH - 120 - BUTTON_PADDING) // 2
        start_y = 350

        for i, option in enumerate(current_q["options"]):
            row = i // 2
            col = i % 2
            button_x = 60 + col * (button_width + BUTTON_PADDING)
            button_y = start_y + row * (QUESTION_BUTTON_HEIGHT + BUTTON_PADDING)
            button = Button(button_x, button_y, button_width, QUESTION_BUTTON_HEIGHT, option, self.button_font)
            self.option_buttons.append(button)

    def handle_answer(self, selected_index):
        current_q = self.questions[self.index]
        self.last_user_answer = selected_index

        if selected_index == current_q["answer"]:
            self.score += 1
            self.feedback_text = f"Correct! {current_q.get('tip', '')}"
            self.feedback_color = CORRECT_COLOR
            current_q['correct'] = 1 # For difficulty adjustment
        else:
            if 'topic' in current_q:
                self.wrong_topics.append(current_q['topic'])
            correct_answer = current_q["options"][current_q["answer"]]
            self.feedback_text = f"Incorrect. The correct answer is: {correct_answer}"
            self.feedback_color = INCORRECT_COLOR
            current_q['correct'] = 0 # For difficulty adjustment

        self.state = "feedback"
        # Removed timer-based advance, user must click to continue

    def get_ai_explanation(self):
        current_q = self.questions[self.index]
        self.ai_explanation = self.ai_assistant.get_detailed_explanation(
            current_q["question"], self.last_user_answer, current_q["answer"], current_q["options"]
        )
        self.state = "ai_explanation"

    def request_study_plan(self):
        if not self.wrong_topics:
            self.study_plan = "You did great! No specific weak areas were identified. Keep up the good work!"
        else:
            unique_weak_topics = list(set(self.wrong_topics))
            self.study_plan = self.ai_assistant.generate_study_plan(unique_weak_topics, self.score)
        self.state = "study_plan"

    def handle_event(self, event):
        if self.state == "home":
            if self.start_button.handle_event(event):
                self.start_quiz(ai_mode=False)
            if self.ai_assistant.model: # Only show AI button if AI is available
                 if self.ai_mode_button.handle_event(event):
                    self.start_quiz(ai_mode=True)
        elif self.state == "question":
            for i, button in enumerate(self.option_buttons):
                if button.handle_event(event):
                    self.handle_answer(i)
                    break
        elif self.state == "feedback":
            # Show AI explanation button only for wrong answers and if AI is available
            if self.last_user_answer != self.questions[self.index]["answer"] and self.ai_assistant.model:
                if self.ai_explanation_button.handle_event(event):
                    self.get_ai_explanation()
            if self.continue_button.handle_event(event):
                self.adjust_difficulty()
                self.next_question()
        elif self.state == "ai_explanation":
            if self.continue_button.handle_event(event):
                self.adjust_difficulty()
                self.next_question()
        elif self.state == "summary":
            if self.retake_button.handle_event(event):
                self.start_quiz(ai_mode=self.ai_mode)
            if self.ai_assistant.model and self.study_plan_button.handle_event(event):
                self.request_study_plan()
        elif self.state == "study_plan":
            if self.retake_button.handle_event(event):
                self.start_quiz(ai_mode=self.ai_mode)

    def draw_home_screen(self):
        self.screen.fill(BACKGROUND_COLOR)
        draw_text_centered(self.screen, "AI-Powered First-Aid Quiz", self.title_font, TITLE_COLOR, 100)
        draw_text_centered(self.screen, "Learn life-saving skills with AI assistance", self.button_font, TEXT_COLOR, 180)
        
        self.start_button.draw(self.screen)
        if self.ai_assistant.model:
            self.ai_mode_button.draw(self.screen)
            draw_text_centered(self.screen, "AI Mode: Personalized questions based on your performance.", self.ai_font, TEXT_COLOR, 540)
        else:
             draw_text_centered(self.screen, "AI features disabled. Check console for API Key instructions.", self.ai_font, INCORRECT_COLOR, 540)
             
    def draw_question_screen(self):
        self.screen.fill(BACKGROUND_COLOR)
        current_q = self.questions[self.index]
        counter_text = f"Question {self.index + 1}/{self.total_questions_in_round}"
        if self.ai_mode:
            counter_text += " (AI Mode)"
        counter_surface = self.counter_font.render(counter_text, True, TEXT_COLOR)
        self.screen.blit(counter_surface, (20, 20))

        draw_text_centered(self.screen, current_q["question"], self.question_font, TEXT_COLOR, 120, max_width=QUESTION_MAX_WIDTH_PX)

        for button in self.option_buttons:
            button.draw(self.screen)

    def draw_feedback_screen(self):
        self.draw_question_screen() # Redraw the question screen as a base
        
        # Overlay for feedback
        s = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180)) # Semi-transparent black overlay
        self.screen.blit(s, (0,0))
        
        draw_text_centered(self.screen, self.feedback_text, self.message_font, self.feedback_color, 280, max_width=WINDOW_WIDTH-100)
        
        # Show AI explanation button only for wrong answers
        if self.last_user_answer != self.questions[self.index]["answer"] and self.ai_assistant.model:
            self.ai_explanation_button.draw(self.screen)
        self.continue_button.draw(self.screen)

    def draw_ai_response_screen(self, title, text_content):
        self.screen.fill(BACKGROUND_COLOR)
        draw_text_centered(self.screen, title, self.title_font, AI_BUTTON_COLOR, 50)
        
        lines = text_content.split('\n')
        wrapped_lines = []
        for line in lines:
            wrapped_lines.extend(wrap_text(line, self.ai_font, WINDOW_WIDTH - 100))

        line_height = self.ai_font.get_height() + 5
        max_lines = (WINDOW_HEIGHT - 300) // line_height
        visible_lines = wrapped_lines[:max_lines]

        draw_multiline_text(self.screen, visible_lines, self.ai_font, TEXT_COLOR, 50, 150, line_height)

        if self.state == "ai_explanation":
             self.continue_button.draw(self.screen)
        else: # Study Plan screen
             self.retake_button.rect.y = WINDOW_HEIGHT - 120 # Move button down
             self.retake_button.draw(self.screen)

    def draw_summary_screen(self):
        self.screen.fill(BACKGROUND_COLOR)
        draw_text_centered(self.screen, "Quiz Complete!", self.title_font, TITLE_COLOR, 80)
        draw_text_centered(self.screen, f"Score: {self.score}/{len(self.questions)}", self.score_font, TEXT_COLOR, 180)

        performance = self.score / len(self.questions)
        message = "Keep practicing! Consider the AI study plan."
        if performance >= 0.8: message = "Excellent! You have strong first-aid knowledge!"
        elif performance >= 0.5: message = "Good job! Review your weak areas for improvement."
        
        draw_text_centered(self.screen, message, self.message_font, TEXT_COLOR, 260, max_width=WINDOW_WIDTH-100)

        if self.wrong_topics:
            weak_text = f"Focus areas: {', '.join(sorted(list(set(self.wrong_topics))))}"
            draw_text_centered(self.screen, weak_text, self.ai_font, TEXT_COLOR, 340, max_width=WINDOW_WIDTH-100)
        
        self.retake_button.rect.y = 460 # Reset position
        self.retake_button.draw(self.screen)
        if self.ai_assistant.model:
            self.study_plan_button.draw(self.screen)

    def draw(self):
        if self.state == "home": self.draw_home_screen()
        elif self.state == "question": self.draw_question_screen()
        elif self.state == "feedback": self.draw_feedback_screen()
        elif self.state == "ai_explanation": self.draw_ai_response_screen("AI Explanation", self.ai_explanation)
        elif self.state == "summary": self.draw_summary_screen()
        elif self.state == "study_plan": self.draw_ai_response_screen("Your AI Study Plan", self.study_plan)
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.handle_event(event)

            self.draw()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()

def main():
    print("Starting AI-Powered First-Aid Quiz Game...")
    game = QuizGame()
    game.run()

if __name__ == "__main__":
    main()