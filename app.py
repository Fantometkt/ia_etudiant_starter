from flask import Flask, render_template, request, jsonify
from utils import *
from safety import sanitize_payload
from memory_manager import *
from generator import generate_answer
from judge import judge
from laboratory.selftest import self_test
from learning_eval import evaluate_student_answer
from progress_engine import compute_progress_delta
from metrics import log_event, build_project_metrics, build_student_dashboard


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    payload = sanitize_payload(data)

    if not payload["message"]:
        return jsonify({
            "ok": False,
            "error": "message_empty",
            "answer": "Écris une question."
        }), 400

    mem = load_memory()

    student_eval = None

    if payload["previous_response"]:
        student_eval = evaluate_student_answer(
            cours=payload["cours"],
            question=payload["message"],
            student_answer=payload["previous_response"],
            niveau=payload["niveau"],
            matiere=payload["matiere"]
        )

    answer = generate_answer(
        mem=mem,
        message=payload["message"],
        niveau=payload["niveau"],
        matiere=payload["matiere"],
        cours=payload["cours"],
        mode=payload["mode"],
        student_id=payload["student_id"],
        learning_style=payload["learning_style"],
        weaknesses=payload["weaknesses"],
        previous_response=payload["previous_response"],
        learning_goal=payload["learning_goal"],
        help_level=payload["help_level"],
        student_eval=student_eval
        fast_eval=bool(data.get("fast_eval", False))
    )

    update_student_memory(
        mem=mem,
        student_id=payload["student_id"],
        display_name=payload["student_name"],
        niveau=payload["niveau"],
        matiere=payload["matiere"],
        learning_style=payload["learning_style"],
        weaknesses=payload["weaknesses"],
        mode=payload["mode"],
        message=payload["message"],
        cours=payload["cours"],
        answer=answer,
        student_eval=student_eval
    )

    save_memory(mem)

    log_event("chat", {
        "student_id": payload["student_id"],
        "mode": payload["mode"],
        "matiere": payload["matiere"],
        "niveau": payload["niveau"],
        "has_course": bool(payload["cours"]),
        "has_student_answer": bool(payload["previous_response"]),
        "student_score": student_eval.get("score") if student_eval else None,
        "injection_flags": payload["injection_flags"]
    })

    return jsonify({
        "ok": True,
        "answer": answer,
        "student_eval": student_eval,
        "injection_flags": payload["injection_flags"]
    })


@app.route("/evaluate", methods=["POST"])
def evaluate():
    data = request.get_json(force=True)
    payload = sanitize_payload(data)

    student_answer = clean(data.get("student_answer")) or payload["previous_response"]

    result = evaluate_student_answer(
        cours=payload["cours"],
        question=payload["message"],
        student_answer=student_answer,
        niveau=payload["niveau"],
        matiere=payload["matiere"]
    )

    log_event("evaluate", {
        "student_id": payload["student_id"],
        "score": result.get("score"),
        "matiere": payload["matiere"],
        "niveau": payload["niveau"]
    })

    return jsonify({
        "ok": True,
        "evaluation": result
    })


@app.route("/progress-check", methods=["POST"])
def progress_check():
    data = request.get_json(force=True)
    payload = sanitize_payload(data)

    pre_answer = clean(data.get("pre_answer"))
    post_answer = clean(data.get("post_answer"))

    if not pre_answer or not post_answer:
        return jsonify({
            "ok": False,
            "error": "pre_answer_and_post_answer_required"
        }), 400

    pre_eval = evaluate_student_answer(
        cours=payload["cours"],
        question=payload["message"],
        student_answer=pre_answer,
        niveau=payload["niveau"],
        matiere=payload["matiere"]
    )

    post_eval = evaluate_student_answer(
        cours=payload["cours"],
        question=payload["message"],
        student_answer=post_answer,
        niveau=payload["niveau"],
        matiere=payload["matiere"]
    )

    delta = compute_progress_delta(
        pre_eval.get("score", 0),
        post_eval.get("score", 0)
    )

    mem = load_memory()

    update_student_memory(
        mem=mem,
        student_id=payload["student_id"],
        display_name=payload["student_name"],
        niveau=payload["niveau"],
        matiere=payload["matiere"],
        learning_style=payload["learning_style"],
        weaknesses=payload["weaknesses"],
        mode="progress_check",
        message=payload["message"],
        cours=payload["cours"],
        answer="Progression mesurée entre pré-test et post-test.",
        student_eval=post_eval,
        pre_post_delta=delta
    )

    save_memory(mem)

    log_event("progress_check", {
        "student_id": payload["student_id"],
        "pre_score": pre_eval.get("score"),
        "post_score": post_eval.get("score"),
        "delta": delta
    })

    return jsonify({
        "ok": True,
        "pre_eval": pre_eval,
        "post_eval": post_eval,
        "delta": delta
    })


@app.route("/student-dashboard", methods=["POST"])
def student_dashboard():
    data = request.get_json(force=True)
    student_id = clean(data.get("student_id")) or "local_student"

    mem = load_memory()
    student = safe_dict(mem.get("students")).get(student_id)

    if not student:
        return jsonify({
            "ok": False,
            "error": "student_not_found"
        }), 404

    return jsonify({
        "ok": True,
        "dashboard": build_student_dashboard(student)
    })


@app.route("/project-metrics", methods=["GET"])
def project_metrics():
    mem = load_memory()

    return jsonify({
        "ok": True,
        "metrics": build_project_metrics(mem)
    })


@app.route("/selftest", methods=["POST"])
def run_test():
    result = self_test(
        load_memory,
        save_memory,
        generate_answer,
        judge
    )

    log_event("selftest", {
        "tests_count": len(result.get("results", [])),
        "diagnostics": result.get("diagnostics", {})
    })

    return jsonify({
        "ok": True,
        "result": result
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "ok": True,
        "status": "running"
    })


if __name__ == "__main__":
    app.run(debug=False, port=8000)