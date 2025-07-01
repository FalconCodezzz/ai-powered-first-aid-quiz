# AI-Powered First-Aid Quiz Game

**Submission for CS Base Hack4Health Hackathon**

## Overview

This project is an interactive, AI-powered quiz game built with Python and Pygame. It teaches users essential first-aid steps through scenario-based questions, instant feedback, and adaptive learning. With optional Google Gemini AI integration, the game can generate personalized questions, explanations, and study plans based on user performance.

## Features

- **Interactive Quiz:** 10-question rounds with multiple-choice, scenario-based questions.
- **Adaptive Difficulty:** The quiz adjusts question difficulty based on your recent answers.
- **AI Personalization (Optional):** If a Gemini API key is provided, the game can:
  - Generate questions tailored to your weak areas.
  - Offer detailed AI explanations for incorrect answers.
  - Create a personalized study plan after the quiz.
- **Instant Feedback:** Immediate tips and correct answers after each question.
- **User-Friendly Interface:** Clean, accessible design using Pygame.

## How to Run

1. **Install dependencies:**
   ```
   pip install pygame python-dotenv google-generativeai
   ```
2. **(Optional) Enable AI features:**
   - Create a `.env` file in the project folder.
   - Add your Gemini API key:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```
3. **Run the game:**
   ```
   python quiz.py
   ```

## Technologies Used

- Python 3
- Pygame
- Google Generative AI (Gemini API)
- dotenv

## Impact

This game helps users learn and retain life-saving first-aid knowledge in a fun, interactive, and personalized way. It’s ideal for anyone looking to improve their emergency response skills.

---

**This project is a submission for the CS Base Hack4Health Hackathon.**
