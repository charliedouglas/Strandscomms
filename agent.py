"""
AI Team Communications Agent
Implements Strands agent for intelligent communication planning and draft generation
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import uuid
from pydantic import BaseModel, Field

# Import Strands SDK
from strands import Agent, tool


DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "projects.json")


# Pydantic models for structured outputs


class PlannedCommunication(BaseModel):
    """Model for a single planned communication"""

    target_date: str = Field(description="Target date in YYYY-MM-DD format")
    type: str = Field(
        description="Type: status_update, launch_announcement, new_features, or management_update"
    )
    audiences: List[str] = Field(
        description="List of audiences: users, developers, management"
    )
    reason: str = Field(description="Justification for this communication")
    key_topics: List[str] = Field(description="Key topics to cover")
    status: str = Field(
        default="pending", description="Status: pending, sent, or cancelled"
    )


class CommsPlan(BaseModel):
    """Model for complete communications plan"""

    generated_date: str = Field(description="Date plan was generated")
    planning_horizon: str = Field(description="Planning horizon (e.g., '3 months')")
    planned_communications: List[PlannedCommunication] = Field(
        description="List of planned communications"
    )


class EmailDraft(BaseModel):
    """Model for email draft"""

    subject: str = Field(description="Email subject line")
    body: str = Field(description="Email body content")
    key_points: List[str] = Field(description="Key points covered in the email")


# Data access functions


def load_projects() -> Dict[str, Any]:
    """Load projects from JSON file"""
    if not os.path.exists(DATA_FILE):
        return {"projects": []}

    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_projects(data: Dict[str, Any]) -> None:
    """Save projects to JSON file"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_project_by_id(project_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific project by ID"""
    data = load_projects()
    for project in data.get("projects", []):
        if project["id"] == project_id:
            return project
    return None


# Tool functions for the agent


@tool
def get_project_context(project_id: str) -> str:
    """
    Get comprehensive project context for planning communications.

    Args:
        project_id: The project identifier

    Returns:
        Formatted string with all project details
    """
    project = get_project_by_id(project_id)
    if not project:
        return "ERROR: Project not found"

    context = f"""
Project: {project['name']}
Status: {project['status']}
Current Phase: {project['current_phase']}
Start Date: {project['start_date']}
Expected Launch: {project['expected_launch']}

Business Value: {project['business_value']}
Description: {project['description']}

Recent Updates:
{chr(10).join('- ' + update for update in project['recent_updates'])}

Upcoming Milestones:
{chr(10).join(f"- {m['date']}: {m['description']}" for m in project['upcoming_milestones'])}

Stakeholders:
- Users: {', '.join(project['stakeholders']['users'])}
- Developers: {', '.join(project['stakeholders']['developers'])}
- Management: {', '.join(project['stakeholders']['management'])}

Previous Communications:
{chr(10).join(f"- {c['date_sent']} ({c['audience']}): {c['subject']}" for c in project['comms_history'])}
    """
    return context.strip()


@tool
def save_communications_plan(project_id: str, plan_json: str) -> str:
    """
    Save a communications plan to a project.

    Args:
        project_id: The project identifier
        plan_json: JSON string containing the communications plan

    Returns:
        Success or error message
    """
    try:
        plan_data = json.loads(plan_json)
        data = load_projects()

        for proj in data["projects"]:
            if proj["id"] == project_id:
                proj["comms_plan"] = plan_data
                save_projects(data)
                return f"SUCCESS: Communications plan saved for project {proj['name']}"

        return "ERROR: Project not found"
    except Exception as e:
        return f"ERROR: {str(e)}"


# Create the agent with proper configuration
COMMS_AGENT_SYSTEM_PROMPT = """You are an expert communications strategist for technical teams.
Your role is to help project teams communicate effectively with different stakeholders:
- Users: Focus on benefits, use accessible language, keep it brief
- Developers: Technical details, architecture, integration points
- Management: Metrics, ROI, risks, resources, strategic value

Maintain communication continuity by referencing previous updates.
Plan communications based on project phase, timeline, and audience needs.

When generating communications plans:
1. Status updates: every 2-4 weeks for active projects
2. Launch announcements: when status changes or launch date reached
3. New features: when milestones indicate feature releases
4. Management updates: monthly
5. Consider communication gaps - identify audiences not communicated with recently
6. Justify each planned communication with clear reasoning
"""

# Initialize the agent with tools
comms_agent = Agent(
    system_prompt=COMMS_AGENT_SYSTEM_PROMPT,
    tools=[get_project_context, save_communications_plan],
    model="eu.anthropic.claude-sonnet-4-20250514-v1:0",  # Bedrock model ID
)


# Main agent functions


def generate_comms_plan(project_id: str) -> Dict[str, Any]:
    """
    Generate a 3-month communications plan for a project using structured output.

    Args:
        project_id: The project identifier

    Returns:
        Updated comms_plan object with planned communications
    """
    project = get_project_by_id(project_id)
    if not project:
        return {"error": "Project not found"}

    today = datetime.now().strftime("%Y-%m-%d")

    prompt = f"""
Analyze this project and create a comprehensive 3-month communications plan.

Use the get_project_context tool to retrieve full project details for project_id: {project_id}

Based on the project context:
- Plan communications for the next 3 months starting from {today}
- Specify target_date in YYYY-MM-DD format
- Choose appropriate type: status_update, launch_announcement, new_features, or management_update
- Select relevant audiences from: users, developers, management
- Provide clear reason for each communication
- List key topics to cover
- Set status to "pending"

Consider:
- Project phase and timeline
- Communication gaps (which audiences haven't been contacted recently)
- Upcoming milestones
- Appropriate cadence for each stakeholder group
"""

    try:
        # Use structured output to get type-safe plan
        plan = comms_agent.structured_output(CommsPlan, prompt)

        # Convert to dict and update project
        plan_data = plan.model_dump()
        plan_data["generated_date"] = today
        plan_data["planning_horizon"] = "3 months"

        data = load_projects()
        for proj in data["projects"]:
            if proj["id"] == project_id:
                proj["comms_plan"] = plan_data
                break

        save_projects(data)
        return plan_data

    except Exception as e:
        print(f"Error generating plan: {e}")
        # Generate fallback plan
        return _generate_fallback_plan(project)


def get_due_communications() -> List[Dict[str, Any]]:
    """
    Find all communications due within the next 7 days.

    Returns:
        List of due communications with project context
    """
    data = load_projects()
    today = datetime.now().date()
    due_date = today + timedelta(days=7)

    due_comms = []

    for project in data.get("projects", []):
        comms_plan = project.get("comms_plan", {})
        planned = comms_plan.get("planned_communications", [])

        for comm in planned:
            if comm.get("status") != "pending":
                continue

            try:
                target_date = datetime.strptime(comm["target_date"], "%Y-%m-%d").date()
                if today <= target_date <= due_date:
                    due_comms.append(
                        {
                            "project_id": project["id"],
                            "project_name": project["name"],
                            "planned_comm": comm,
                            "days_until_due": (target_date - today).days,
                        }
                    )
            except (ValueError, KeyError) as e:
                print(f"Error parsing date for communication: {e}")
                continue

    # Sort by due date
    due_comms.sort(key=lambda x: x["days_until_due"])

    return due_comms


def generate_email_draft(
    project_id: str, planned_comm_id: str = None, planned_comm: Dict[str, Any] = None
) -> List[Dict[str, Any]]:
    """
    Generate email drafts for a planned communication using structured output.
    Creates separate drafts for each audience.

    Args:
        project_id: The project identifier
        planned_comm_id: Target date of planned communication (optional)
        planned_comm: The planned communication object (optional)

    Returns:
        List of draft email objects (one per audience)
    """
    project = get_project_by_id(project_id)
    if not project:
        return [{"error": "Project not found"}]

    # Find the planned communication
    if not planned_comm:
        for comm in project.get("comms_plan", {}).get("planned_communications", []):
            if comm.get("target_date") == planned_comm_id:
                planned_comm = comm
                break

    if not planned_comm:
        return [{"error": "Planned communication not found"}]

    drafts = []

    # Audience-specific instructions
    audience_guidelines = {
        "users": """
        - Focus on benefits and user value
        - Use accessible, non-technical language
        - Keep it brief (under 200 words)
        - Highlight what's in it for them
        - Use friendly, engaging tone
        """,
        "developers": """
        - Include technical details and architecture
        - Mention integration points and APIs
        - Discuss implementation specifics
        - Keep under 300 words
        - Use technical terminology appropriately
        """,
        "management": """
        - Focus on metrics, ROI, and strategic value
        - Mention risks and resource requirements
        - Include timeline and budget status
        - Keep under 250 words
        - Professional, executive tone
        """,
    }

    # Generate draft for each audience
    for audience in planned_comm.get("audiences", []):
        # Get communication history for this audience
        audience_history = [
            c for c in project.get("comms_history", []) if c.get("audience") == audience
        ]

        # Prepare context
        context = f"""
Project: {project['name']}
Current Phase: {project['current_phase']}
Status: {project['status']}

Communication Type: {planned_comm['type']}
Target Audience: {audience}
Reason for Communication: {planned_comm['reason']}
Key Topics to Cover: {', '.join(planned_comm.get('key_topics', []))}

Recent Project Updates:
{chr(10).join('- ' + update for update in project['recent_updates'])}

Upcoming Milestones:
{chr(10).join(f"- {m['date']}: {m['description']}" for m in project['upcoming_milestones'])}

Previous Communications to {audience}:
{chr(10).join(f"- {c['date_sent']}: {c['subject']}" for c in audience_history[-3:])}
"""

        prompt = f"""
Write an email for this project communication.

{context}

Audience Guidelines for {audience}:
{audience_guidelines.get(audience, '')}

Additional Requirements:
- Reference previous communications if relevant (maintain continuity)
- Cover the key topics listed
- Match the communication type ({planned_comm['type']})
- Be specific and actionable
"""

        try:
            # Use structured output for type-safe email draft
            draft = comms_agent.structured_output(EmailDraft, prompt)

            draft_data = draft.model_dump()
            draft_data["audience"] = audience
            draft_data["project_id"] = project_id
            draft_data["planned_comm_id"] = planned_comm_id or planned_comm.get(
                "target_date"
            )
            draft_data["type"] = planned_comm["type"]
            draft_data["draft_id"] = str(uuid.uuid4())

            drafts.append(draft_data)

        except Exception as e:
            print(f"Error generating draft for {audience}: {e}")
            # Fallback draft
            drafts.append(_generate_fallback_draft(project, audience, planned_comm))

    return drafts


def update_comms_history(project_id: str, comm_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update project communications history after sending.

    Args:
        project_id: The project identifier
        comm_data: Communication details to add to history

    Returns:
        Success confirmation
    """
    data = load_projects()

    for project in data["projects"]:
        if project["id"] == project_id:
            # Add to comms history
            comm_entry = {
                "id": comm_data.get("id", f"comm_{str(uuid.uuid4())[:8]}"),
                "date_sent": comm_data.get(
                    "date_sent", datetime.now().strftime("%Y-%m-%d")
                ),
                "type": comm_data.get("type"),
                "audience": comm_data.get("audience"),
                "subject": comm_data.get("subject"),
                "summary": comm_data.get("summary", ""),
                "key_messages": comm_data.get("key_messages", []),
                "sent_to": comm_data.get("sent_to", []),
            }

            if "comms_history" not in project:
                project["comms_history"] = []

            project["comms_history"].append(comm_entry)

            # Update corresponding planned communication status
            target_date = comm_data.get("planned_comm_id")
            if target_date:
                for comm in project.get("comms_plan", {}).get(
                    "planned_communications", []
                ):
                    if comm.get("target_date") == target_date and comm_data.get(
                        "audience"
                    ) in comm.get("audiences", []):
                        comm["status"] = "sent"

            save_projects(data)
            return {
                "success": True,
                "message": f"Communication added to history for project {project['name']}",
            }

    return {"success": False, "error": "Project not found"}


# Helper functions


def _generate_fallback_plan(project: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a basic fallback communications plan"""
    today = datetime.now()
    planned = []

    # Generate basic plan based on project status
    if project["status"] == "active":
        # Weekly status updates for next 3 months
        for week in range(2, 13, 3):
            date = (today + timedelta(weeks=week)).strftime("%Y-%m-%d")
            planned.append(
                {
                    "target_date": date,
                    "type": "status_update",
                    "audiences": ["developers"],
                    "reason": f"Regular status update - week {week}",
                    "key_topics": ["Progress update", "Blockers", "Next steps"],
                    "status": "pending",
                }
            )

        # Monthly management updates
        for month in [1, 2, 3]:
            date = (today + timedelta(days=30 * month)).strftime("%Y-%m-%d")
            planned.append(
                {
                    "target_date": date,
                    "type": "management_update",
                    "audiences": ["management"],
                    "reason": f"Monthly executive update",
                    "key_topics": ["Progress", "Budget", "Risks", "Timeline"],
                    "status": "pending",
                }
            )

    return {
        "generated_date": today.strftime("%Y-%m-%d"),
        "planning_horizon": "3 months",
        "planned_communications": planned,
    }


def _generate_fallback_draft(
    project: Dict[str, Any], audience: str, planned_comm: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate a basic fallback email draft"""
    subject_templates = {
        "users": f"{project['name']} Update - New Features & Improvements",
        "developers": f"{project['name']} - Technical Update",
        "management": f"{project['name']} Status Report",
    }

    body_templates = {
        "users": f"""
Hi team,

We wanted to share an update on {project['name']}.

Recent progress:
{chr(10).join('- ' + update for update in project['recent_updates'][:3])}

What's coming next:
We're working on {project['current_phase']} and expect to launch on {project['expected_launch']}.

Thanks for your continued support!
        """,
        "developers": f"""
Team,

Technical update on {project['name']}:

Current Phase: {project['current_phase']}

Recent Updates:
{chr(10).join('- ' + update for update in project['recent_updates'][:3])}

Upcoming Milestones:
{chr(10).join(f"- {m['date']}: {m['description']}" for m in project['upcoming_milestones'][:2])}

Please review and let me know if you have questions.
        """,
        "management": f"""
Executive Update: {project['name']}

Status: {project['status']}
Current Phase: {project['current_phase']}
Expected Launch: {project['expected_launch']}

Key Accomplishments:
{chr(10).join('- ' + update for update in project['recent_updates'][:3])}

Business Value: {project['business_value']}

Next Steps:
{chr(10).join(f"- {m['description']}" for m in project['upcoming_milestones'][:2])}
        """,
    }

    return {
        "subject": subject_templates.get(audience, f"{project['name']} Update"),
        "body": body_templates.get(audience, f"Update on {project['name']}").strip(),
        "key_points": planned_comm.get("key_topics", []),
        "audience": audience,
        "draft_id": str(uuid.uuid4()),
    }
