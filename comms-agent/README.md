# AI Team Communications Agent

An intelligent agent that helps teams plan and manage communications for technical projects using AWS Strands SDK and Claude AI.

## Features

- **Project Management**: Track multiple projects with stakeholders, milestones, and status
- **AI-Powered Communications Planning**: Automatically generate 3-month communication plans
- **Smart Email Drafting**: Create audience-specific email drafts (users, developers, management)
- **Due Communications Tracking**: Monitor and manage upcoming communications
- **Communications History**: Track all past communications per project

## Tech Stack

- Python 3.10+
- Flask (backend + frontend)
- AWS Strands SDK (AI agent implementation)
- JSON file storage (no database required)

## Project Structure

```
comms-agent/
├── app.py                 # Flask application with all endpoints
├── agent.py              # Strands AI agent implementation
├── data/
│   └── projects.json     # Project data storage
├── templates/
│   ├── index.html       # Dashboard
│   ├── project.html     # Project details view
│   ├── plan.html        # Communications plan view
│   ├── due_comms.html   # Due communications view
│   └── create_project.html  # Project creation form
├── static/
│   └── style.css        # Application styling
└── requirements.txt     # Python dependencies
```

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd comms-agent
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up AWS credentials** (required for Strands SDK):
   Ensure your AWS credentials are configured with access to Claude AI:
   ```bash
   aws configure
   ```

## Usage

1. **Start the application**:
   ```bash
   python app.py
   ```

2. **Access the web interface**:
   Open your browser to: `http://localhost:5000`

3. **Key workflows**:

   - **View Dashboard**: See all projects and their status
   - **Create Project**: Add a new project with stakeholders and milestones
   - **Generate Comms Plan**: Let AI analyze the project and create a 3-month communication plan
   - **Check Due Communications**: View all communications due in the next 7 days
   - **Generate Email Drafts**: AI creates audience-specific email drafts
   - **Review & Approve**: Edit and approve drafts before marking them as sent

## Agent Capabilities

### 1. Generate Communications Plan
- Analyzes project timeline, status, and milestones
- Identifies communication gaps
- Recommends optimal communication cadence
- Plans 3 months of communications with justification

### 2. Get Due Communications
- Scans all projects for upcoming communications
- Returns communications due within 7 days
- Prioritizes by urgency

### 3. Generate Email Drafts
- Creates audience-specific drafts (users, developers, management)
- Maintains communication continuity
- Follows tone and length guidelines:
  - Users: Benefits-focused, under 200 words
  - Developers: Technical details, under 300 words
  - Management: Metrics and ROI, under 250 words

### 4. Update Communications History
- Tracks all sent communications
- Updates communication plan status
- Maintains historical context for future communications

## Sample Data

The application comes with 2 sample projects:

1. **Customer Portal Redesign** (Active): A project in development with communication history
2. **AI-Powered Document Search** (Planning): A new project with no communications yet

## API Endpoints

- `GET /` - Dashboard
- `GET /project/<id>` - Project details
- `POST /project/create` - Create new project
- `POST /project/<id>/edit` - Update project
- `POST /project/<id>/generate-plan` - Generate communications plan
- `GET /due-comms` - View due communications
- `POST /generate-drafts` - Generate email drafts
- `POST /send-email` - Mark email as sent and update history

## Configuration

No additional configuration required for local development. The application uses:

- Flask development server on port 5000
- JSON file storage in `data/projects.json`
- AWS Strands SDK with default Claude model

## Development Notes

- No authentication/authorization (single-user application)
- No actual email sending (draft generation only)
- Data persists in JSON file
- Uses Claude 3.5 Sonnet via Strands SDK for AI capabilities

## Success Criteria

✅ Create/edit projects via web interface
✅ Agent generates realistic 3-month comms plan
✅ Agent identifies communications due this week
✅ Agent generates audience-appropriate email drafts
✅ Review and approve drafts via web interface
✅ Communications history updates after approval
✅ All data persists in projects.json

## License

Internal use only.
