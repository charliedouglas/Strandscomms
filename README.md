# AI Team Communications Agent

An intelligent agent that helps teams plan and manage communications for technical projects using **AWS Strands Agents SDK** and **Claude AI** via Amazon Bedrock.

## ✨ Features

- **🤖 AI-Powered Draft Generation**: Generate audience-specific email drafts in seconds
- **📋 Smart Planning**: Automatically create 3-month communication plans
- **🎯 Audience Targeting**: Different tones for users, developers, and management
- **📊 Project Management**: Track multiple projects with stakeholders and milestones
- **📅 Due Communications**: Monitor and manage upcoming communications
- **📜 Communications History**: Track all past communications per project
- **🔄 Structured Outputs**: Type-safe AI responses using Pydantic models

## 🚀 Quick Start

**See [QUICK_START.md](QUICK_START.md) for a 5-minute setup guide!**

## 🛠️ Tech Stack

- **Python 3.10+** - Core language
- **Flask 3.0.0** - Web framework
- **AWS Strands SDK** - AI agent implementation (refactored to SDK best practices)
- **Pydantic 2.0+** - Data validation and structured outputs
- **Amazon Bedrock** - Claude AI model hosting
- **JSON file storage** - No database required (dev mode)

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

## 🤖 AI Agent Capabilities

### 1. Generate Communications Plan
- ✅ Uses **structured outputs** with Pydantic models for type safety
- ✅ Analyzes project timeline, status, and milestones via tool calls
- ✅ Identifies communication gaps across stakeholder groups
- ✅ Recommends optimal communication cadence
- ✅ Plans 3 months of communications with clear justification

### 2. Get Due Communications
- ✅ Scans all projects for upcoming communications
- ✅ Returns communications due within 7 days
- ✅ Prioritizes by urgency (days until due)

### 3. Generate Email Drafts ⭐ **NEW & ENHANCED**
- ✅ **AI-powered** draft generation using Claude via Bedrock
- ✅ Creates **audience-specific** drafts with tailored tone and content
- ✅ Maintains communication **continuity** with project history
- ✅ Follows strict **tone and length guidelines**:
  - **Users**: Benefits-focused, non-technical, <200 words, friendly
  - **Developers**: Technical details, architecture, <300 words, professional
  - **Management**: Metrics/ROI, strategic value, <250 words, executive
- ✅ **Editable** drafts before sending
- ✅ **Copy to clipboard** functionality
- ✅ Real-time **loading states** and notifications

### 4. Update Communications History
- ✅ Tracks all sent communications
- ✅ Updates communication plan status to "sent"
- ✅ Maintains historical context for future communications

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

## ✅ Success Criteria

✅ Create/edit projects via web interface
✅ Agent generates realistic 3-month comms plan
✅ Agent identifies communications due this week
✅ **Agent generates audience-appropriate email drafts using structured outputs**
✅ **Real-time UI feedback with loading states and notifications**
✅ **Copy drafts to clipboard for easy transfer**
✅ Review and approve drafts via enhanced modal interface
✅ Communications history updates after approval
✅ **Plan status updates to "sent" automatically**
✅ All data persists in projects.json
✅ **Type-safe AI responses with Pydantic validation**

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)** - Get started in 5 minutes
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Comprehensive testing instructions
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical implementation details

## 🔧 Recent Updates (Oct 28, 2025)

### Major Refactor: Strands SDK Best Practices
- ✅ Refactored agent to use proper Strands SDK patterns
- ✅ Removed invalid class inheritance
- ✅ Implemented structured outputs with Pydantic models
- ✅ Added proper `@tool` decorated functions
- ✅ Fixed Bedrock model ID format
- ✅ Enhanced UI with notifications and loading states
- ✅ Added copy-to-clipboard functionality
- ✅ Improved error handling throughout

## 🐛 Known Limitations

- Single-user application (no authentication)
- File-based storage (not suitable for production scale)
- No actual email sending (simulation only)
- Requires AWS Bedrock access with Claude model

## 🚀 Future Enhancements

- [ ] Multi-user authentication
- [ ] Database integration (PostgreSQL/DynamoDB)
- [ ] Actual email sending via SES
- [ ] Email template library
- [ ] Analytics dashboard
- [ ] Notification scheduling
- [ ] Mobile app

## 📄 License

Internal use only.
