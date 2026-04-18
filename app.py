from utils import *
from memory_manager import *
from generator import generate_answer
from judge import judge
from selftest import self_test

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# =========================================================
# ROUTES
# =========================================================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    message = clean(data.get("message"))
    niveau = clean(data.get("niveau")) or "L1"
    matiere = clean(data.get("matiere"))
    cours = clean(data.get("cours"))
    mode = clean(data.get("mode")) or "expliquer"

    student_id = clean(data.get("student_id"))
    display_name = clean(data.get("student_name"))
    learning_style = clean(data.get("learning_style"))
    weaknesses = clean(data.get("weaknesses"))
    previous_response = clean(data.get("previous_response"))

    learning_goal = clean(data.get("learning_goal")) or "comprendre"
    help_level = clean(data.get("help_level")) or "equilibre"

    if not message:
        return jsonify({"answer": "Écris une question."})

    try:
        mem = load_memory()

        answer = generate_answer(
            mem=mem,
            message=message,
            niveau=niveau,
            matiere=matiere,
            cours=cours,
            mode=mode,
            student_id=student_id,
            learning_style=learning_style,
            weaknesses=weaknesses,
            previous_response=previous_response,
            learning_goal=learning_goal,
            help_level=help_level
        )

        update_student_memory(
            mem=mem,
            student_id=student_id,
            display_name=display_name,
            niveau=niveau,
            matiere=matiere,
            learning_style=learning_style,
            weaknesses=weaknesses,
            mode=mode,
            message=message,
            cours=cours,
            answer=answer
        )

        save_memory(mem)

        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"answer": f"Erreur : {str(e)}"})

@app.route("/selftest", methods=["POST"])
def run_test():
    return jsonify(self_test(load_memory, save_memory, generate_answer, judge))

@app.route("/memory")
def memory():
    return jsonify(load_memory())

@app.route("/student-memory", methods=["POST"])
def student_memory():
    data = request.get_json(force=True)
    student_id = clean(data.get("student_id"))

    if not student_id:
        return jsonify({"error": "student_id manquant"}), 400

    mem = load_memory()
    student = mem.get("students", {}).get(student_id)

    if not student:
        return jsonify({"error": "Mémoire étudiante introuvable"}), 404

    return jsonify(student)

if __name__ == "__main__":
    app.run(debug=True, port=8000)