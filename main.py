import os
from flask import Flask, jsonify, request
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools

# --- CONFIGURATION ---
GOOGLE_API_KEY = "AIzaSyCE3KrmeeDbIDDPLQaR5z8Nf0izmKVxzOI"
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# --- DEFINE AGENTS ---

# Dietary Planner Agent
dietary_planner = Agent(
    model=Gemini(id="gemini-2.0-flash-exp"),
    description="Creates personalized dietary plans based on user input.",
    instructions=[
        "Generate a diet plan with breakfast, lunch, dinner, and snacks.",
        "Consider dietary preferences like Keto, Vegetarian, or Low Carb.",
        "Ensure proper hydration and electrolyte balance.",
        "Provide nutritional breakdown including macronutrients and vitamins.",
        "Suggest meal preparation tips for easy implementation.",
        "If necessary, search the web using DuckDuckGo for additional information.",
    ],
    tools=[DuckDuckGoTools()],
    markdown=True
)

# Fitness Trainer Agent
fitness_trainer = Agent(
    model=Gemini(id="gemini-2.0-flash-exp"),
    description="Generates customized workout routines based on fitness goals.",
    instructions=[
        "Create a workout plan including warm-ups, main exercises, and cool-downs.",
        "Adjust workouts based on fitness level: Beginner, Intermediate, Advanced.",
        "Consider weight loss, muscle gain, endurance, or flexibility goals.",
        "Provide safety tips and injury prevention advice.",
        "Suggest progress tracking methods for motivation.",
        "If necessary, search the web using DuckDuckGo for additional information.",
    ],
    tools=[DuckDuckGoTools()],
    markdown=True
)

# Team Lead Agent (Combines both)
team_lead = Agent(
    model=Gemini(id="gemini-2.0-flash-exp"),
    description="Combines diet and workout plans into a holistic health strategy.",
    instructions=[
        "Merge personalized diet and fitness plans for a comprehensive approach, Use Tables if possible.",
        "Ensure alignment between diet and exercise for optimal results.",
        "Suggest lifestyle tips for motivation and consistency.",
        "Provide guidance on tracking progress and adjusting plans over time."
    ],
    markdown=True
)

# --- HELPER FUNCTIONS ---
def get_meal_plan(age, weight, height, activity_level, dietary_preference, fitness_goal):
    prompt = (
        f"Create a personalized meal plan for a {age}-year-old person, weighing {weight}kg, "
        f"{height}cm tall, with an activity level of '{activity_level}', following a "
        f"'{dietary_preference}' diet, aiming to achieve '{fitness_goal}'."
    )
    return dietary_planner.run(prompt)

def get_fitness_plan(age, weight, height, activity_level, fitness_goal):
    prompt = (
        f"Generate a workout plan for a {age}-year-old person, weighing {weight}kg, "
        f"{height}cm tall, with an activity level of '{activity_level}', "
        f"aiming to achieve '{fitness_goal}'. Include warm-ups, exercises, and cool-downs."
    )
    return fitness_trainer.run(prompt)

def get_full_health_plan(name, age, weight, height, activity_level, dietary_preference, fitness_goal):
    meal_plan = get_meal_plan(age, weight, height, activity_level, dietary_preference, fitness_goal)
    fitness_plan = get_fitness_plan(age, weight, height, activity_level, fitness_goal)

    return team_lead.run(
        f"Greet the customer, {name}.\n\n"
        f"User Information: {age} years old, {weight}kg, {height}cm, activity level: {activity_level}.\n\n"
        f"Fitness Goal: {fitness_goal}\n\n"
        f"Meal Plan:\n{meal_plan}\n\n"
        f"Workout Plan:\n{fitness_plan}\n\n"
        f"Provide a holistic health strategy integrating both plans."
    )

# --- FLASK APP SETUP ---
app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Welcome to AI Health & Fitness Planner API 💪"})

@app.route("/meal-plan", methods=["POST"])
def meal_plan():
    data = request.get_json()
    try:
        response = get_meal_plan(
            data.get("age"),
            data.get("weight"),
            data.get("height"),
            data.get("activity_level"),
            data.get("dietary_preference", "Balanced"),
            data.get("fitness_goal"),
        )
        return jsonify({"meal_plan": response.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/fitness-plan", methods=["POST"])
def fitness_plan():
    data = request.get_json()
    try:
        response = get_fitness_plan(
            data.get("age"),
            data.get("weight"),
            data.get("height"),
            data.get("activity_level"),
            data.get("fitness_goal"),
        )
        return jsonify({"fitness_plan": response.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/full-health-plan", methods=["POST"])
def full_health_plan():
    data = request.get_json()
    try:
        response = get_full_health_plan(
            data.get("name", "John Doe"),
            data.get("age"),
            data.get("weight"),
            data.get("height"),
            data.get("activity_level"),
            data.get("dietary_preference", "Balanced"),
            data.get("fitness_goal"),
        )
        return jsonify({"full_health_plan": response.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- RUN LOCALLY ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
