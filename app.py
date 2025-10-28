"""
Flask application for AI Team Communications Agent
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
import uuid
from datetime import datetime

# Import agent functions
import agent

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-key-change-in-production"

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "projects.json")


# Helper functions


def load_projects():
    """Load projects from JSON file"""
    return agent.load_projects()


def save_projects(data):
    """Save projects to JSON file"""
    agent.save_projects(data)


def get_project_by_id(project_id):
    """Get a specific project by ID"""
    return agent.get_project_by_id(project_id)


# Routes


@app.route("/")
def index():
    """Dashboard: Display all projects"""
    data = load_projects()
    projects = data.get("projects", [])

    # Add last communication date to each project
    for project in projects:
        comms_history = project.get("comms_history", [])
        if comms_history:
            project["last_comm_date"] = comms_history[-1].get("date_sent", "N/A")
        else:
            project["last_comm_date"] = "No communications yet"

    return render_template("index.html", projects=projects)


@app.route("/project/<project_id>")
def project_detail(project_id):
    """Display single project details"""
    project = get_project_by_id(project_id)

    if not project:
        return "Project not found", 404

    return render_template("project.html", project=project)


@app.route("/project/create", methods=["GET", "POST"])
def create_project():
    """Create new project"""
    if request.method == "GET":
        return render_template("create_project.html")

    # Handle POST request
    data = load_projects()

    new_project = {
        "id": f"proj_{str(uuid.uuid4())[:8]}",
        "name": request.form.get("name", ""),
        "owner": request.form.get("owner", ""),
        "status": request.form.get("status", "planning"),
        "description": request.form.get("description", ""),
        "business_value": request.form.get("business_value", ""),
        "start_date": request.form.get(
            "start_date", datetime.now().strftime("%Y-%m-%d")
        ),
        "current_phase": request.form.get("current_phase", ""),
        "expected_launch": request.form.get("expected_launch", ""),
        "stakeholders": {
            "users": [
                email.strip()
                for email in request.form.get("users", "").split(",")
                if email.strip()
            ],
            "developers": [
                email.strip()
                for email in request.form.get("developers", "").split(",")
                if email.strip()
            ],
            "management": [
                email.strip()
                for email in request.form.get("management", "").split(",")
                if email.strip()
            ],
        },
        "recent_updates": [
            update.strip()
            for update in request.form.get("recent_updates", "").split("\n")
            if update.strip()
        ],
        "upcoming_milestones": [],
        "comms_history": [],
        "comms_plan": {
            "generated_date": None,
            "planning_horizon": None,
            "planned_communications": [],
        },
    }

    # Parse milestones if provided
    milestones_data = request.form.get("milestones", "")
    if milestones_data:
        for line in milestones_data.split("\n"):
            if ":" in line:
                parts = line.split(":", 1)
                milestone_date = parts[0].strip()
                milestone_desc = parts[1].strip()
                new_project["upcoming_milestones"].append(
                    {"date": milestone_date, "description": milestone_desc}
                )

    data["projects"].append(new_project)
    save_projects(data)

    return redirect(url_for("project_detail", project_id=new_project["id"]))


@app.route("/project/<project_id>/edit", methods=["POST"])
def edit_project(project_id):
    """Update project details"""
    data = load_projects()

    for project in data["projects"]:
        if project["id"] == project_id:
            # Update fields
            project["name"] = request.form.get("name", project["name"])
            project["owner"] = request.form.get("owner", project["owner"])
            project["status"] = request.form.get("status", project["status"])
            project["description"] = request.form.get(
                "description", project["description"]
            )
            project["business_value"] = request.form.get(
                "business_value", project["business_value"]
            )
            project["current_phase"] = request.form.get(
                "current_phase", project["current_phase"]
            )
            project["expected_launch"] = request.form.get(
                "expected_launch", project["expected_launch"]
            )

            # Update stakeholders
            project["stakeholders"] = {
                "users": [
                    email.strip()
                    for email in request.form.get("users", "").split(",")
                    if email.strip()
                ],
                "developers": [
                    email.strip()
                    for email in request.form.get("developers", "").split(",")
                    if email.strip()
                ],
                "management": [
                    email.strip()
                    for email in request.form.get("management", "").split(",")
                    if email.strip()
                ],
            }

            # Update recent updates
            updates_text = request.form.get("recent_updates", "")
            if updates_text:
                project["recent_updates"] = [
                    u.strip() for u in updates_text.split("\n") if u.strip()
                ]

            # Update milestones
            milestones_data = request.form.get("milestones", "")
            if milestones_data:
                project["upcoming_milestones"] = []
                for line in milestones_data.split("\n"):
                    if ":" in line:
                        parts = line.split(":", 1)
                        milestone_date = parts[0].strip()
                        milestone_desc = parts[1].strip()
                        project["upcoming_milestones"].append(
                            {"date": milestone_date, "description": milestone_desc}
                        )

            save_projects(data)
            break

    return redirect(url_for("project_detail", project_id=project_id))


@app.route("/project/<project_id>/generate-plan", methods=["POST"])
def generate_plan(project_id):
    """Generate communications plan for project"""
    try:
        # Call agent to generate plan
        plan = agent.generate_comms_plan(project_id)

        if "error" in plan:
            return jsonify({"success": False, "error": plan["error"]}), 400

        return jsonify(
            {
                "success": True,
                "plan": plan,
                "message": "Communications plan generated successfully",
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/project/<project_id>/plan")
def view_plan(project_id):
    """View communications plan for project"""
    project = get_project_by_id(project_id)

    if not project:
        return "Project not found", 404

    return render_template("plan.html", project=project)


@app.route("/due-comms")
def due_communications():
    """Show communications due this week"""
    try:
        due_comms = agent.get_due_communications()

        return render_template("due_comms.html", due_communications=due_comms)

    except Exception as e:
        return f"Error fetching due communications: {str(e)}", 500


@app.route("/generate-drafts", methods=["POST"])
def generate_drafts():
    """Generate email drafts for planned communications"""
    try:
        # Get selected communications from request
        selected = request.json.get("communications", [])

        all_drafts = []

        for comm_item in selected:
            project_id = comm_item.get("project_id")
            planned_comm = comm_item.get("planned_comm")

            if not project_id or not planned_comm:
                continue

            # Generate drafts for this communication
            drafts = agent.generate_email_draft(
                project_id=project_id, planned_comm=planned_comm
            )

            all_drafts.extend(drafts)

        return jsonify(
            {
                "success": True,
                "drafts": all_drafts,
                "message": f"Generated {len(all_drafts)} draft(s)",
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/review-drafts")
def review_drafts():
    """Display draft review interface"""
    # Get drafts from session or query params
    # For now, redirect to due communications
    return redirect(url_for("due_communications"))


@app.route("/send-email", methods=["POST"])
def send_email():
    """Mark email as sent and update communications history"""
    try:
        draft_data = request.json

        project_id = draft_data.get("project_id")
        audience = draft_data.get("audience")
        subject = draft_data.get("subject")
        body = draft_data.get("body")
        key_points = draft_data.get("key_points", [])
        planned_comm_id = draft_data.get("planned_comm_id")

        # Get project to find stakeholder emails
        project = get_project_by_id(project_id)
        if not project:
            return jsonify({"success": False, "error": "Project not found"}), 404

        sent_to = project.get("stakeholders", {}).get(audience, [])

        # Create communication history entry
        comm_data = {
            "id": f"comm_{str(uuid.uuid4())[:8]}",
            "date_sent": datetime.now().strftime("%Y-%m-%d"),
            "type": draft_data.get("type", "status_update"),
            "audience": audience,
            "subject": subject,
            "summary": body[:200] + "..." if len(body) > 200 else body,
            "key_messages": key_points,
            "sent_to": sent_to,
            "planned_comm_id": planned_comm_id,
        }

        # Update history via agent
        result = agent.update_comms_history(project_id, comm_data)

        if result.get("success"):
            return jsonify(
                {"success": True, "message": "Email marked as sent and history updated"}
            )
        else:
            return (
                jsonify(
                    {"success": False, "error": result.get("error", "Unknown error")}
                ),
                500,
            )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/project/<project_id>/add-manual-comm", methods=["POST"])
def add_manual_communication(project_id):
    """Add a manual communication to project history"""
    try:
        comm_data = {
            "id": f"comm_{str(uuid.uuid4())[:8]}",
            "date_sent": request.form.get(
                "date_sent", datetime.now().strftime("%Y-%m-%d")
            ),
            "type": request.form.get("type", "status_update"),
            "audience": request.form.get("audience", "users"),
            "subject": request.form.get("subject", ""),
            "summary": request.form.get("summary", ""),
            "key_messages": [
                msg.strip()
                for msg in request.form.get("key_messages", "").split("\n")
                if msg.strip()
            ],
            "sent_to": [
                email.strip()
                for email in request.form.get("sent_to", "").split(",")
                if email.strip()
            ],
        }

        result = agent.update_comms_history(project_id, comm_data)

        if result.get("success"):
            return redirect(url_for("project_detail", project_id=project_id))
        else:
            return f"Error: {result.get('error', 'Unknown error')}", 500

    except Exception as e:
        return f"Error adding communication: {str(e)}", 500


@app.route("/api/projects")
def api_projects():
    """API endpoint to get all projects"""
    data = load_projects()
    return jsonify(data)


@app.route("/api/project/<project_id>")
def api_project(project_id):
    """API endpoint to get single project"""
    project = get_project_by_id(project_id)
    if project:
        return jsonify(project)
    else:
        return jsonify({"error": "Project not found"}), 404


# Error handlers


@app.errorhandler(404)
def not_found(e):
    return "Page not found", 404


@app.errorhandler(500)
def server_error(e):
    return f"Server error: {str(e)}", 500


if __name__ == "__main__":
    # Ensure data directory exists
    os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)

    # Run the app
    print("Starting AI Team Communications Agent...")
    print("Access at: http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5001)
