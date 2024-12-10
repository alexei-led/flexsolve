# AWS Support System

An intelligent AWS support system using AutoGen agents to provide contextual AWS support through specialized researchers and solution providers.

## Overview

This system uses multiple AI agents to:

1. Analyze user questions about AWS services
2. Gather necessary context through researchers
3. Provide detailed solutions through specialists
4. Format responses for optimal readability
5. Collect user satisfaction metrics

## Architecture

### Component Structure

```
aws_support_system/
├── specialists/
│   ├── __init__.py
│   ├── base_specialist.py
│   ├── eks_specialist.py
│   ├── ec2_specialist.py
│   ├── vpc_specialist.py
│   ├── iam_specialist.py
│   ├── cloudwatch_specialist.py
│   ├── lambda_specialist.py
│   ├── ecs_specialist.py
│   ├── s3_specialist.py
│   ├── sns_specialist.py
│   ├── sqs_specialist.py
│   ├── rds_specialist.py
│   ├── elasticache_specialist.py
│   └── aurora_specialist.py
├── researchers/
│   ├── __init__.py
│   ├── base_researcher.py
│   ├── eks_researcher.py
│   ├── ec2_researcher.py
│   ├── vpc_researcher.py
│   ├── iam_researcher.py
│   ├── cloudwatch_researcher.py
│   ├── lambda_researcher.py
│   ├── ecs_researcher.py
│   ├── s3_researcher.py
│   ├── sns_researcher.py
│   ├── sqs_researcher.py
│   ├── rds_researcher.py
│   ├── elasticache_researcher.py
│   └── aurora_researcher.py
├── utils/
│   └── input_handler.py
├── config.py
├── chat_manager.py
└── main.py
```

### Conversation Flow

```mermaid
sequenceDiagram
    actor User
    participant UP as User Proxy
    participant RC as Research Coordinator
    participant RG as Research Group
    participant HE as Human Expert
    participant SC as Solution Coordinator
    participant SG as Specialist Group
    participant SV as Surveyer

    User->>UP: Initial Query
    
    %% Research Phase
    UP->>RC: Forward Query
    RC->>RG: Request Context Questions
    RG-->>RC: Provide Questions
    RC->>HE: Review Questions
    alt Questions Need Work
        HE-->>RC: REWORK + Feedback
        RC->>RG: Request Revision
        RG-->>RC: Updated Questions
        RC->>HE: Review Again
    else Questions Approved
        HE-->>RC: APPROVE
    end
    RC->>UP: Present Questions
    UP->>User: Ask Clarifying Questions
    User->>UP: Provide Context
    
    %% Solution Phase
    UP->>SC: Forward Context
    SC->>SG: Request Solutions
    SG-->>SC: Provide Solutions
    SC->>HE: Review Solutions
    alt Solutions Need Work
        HE-->>SC: REWORK + Feedback
        SC->>SG: Request Revision
        SG-->>SC: Updated Solutions
        SC->>HE: Review Again
    else Solutions Approved
        HE-->>SC: APPROVE
    end
    SC->>UP: Present Solutions
    UP->>User: Present Final Solutions
    
    %% Survey Phase
    UP->>SV: Request Satisfaction Survey
    SV->>User: Ask Rating (1-10)
    User->>SV: Provide Rating
```

### Chat Architecture

```mermaid
graph TB
    subgraph User["User Interaction Layer"]
        U[User]
        UP[User Proxy]
    end

    subgraph Main["Main Chat Layer"]
        RC[Research Coordinator]
        SC[Solution Coordinator]
        SV[Surveyer]
    end

    subgraph Research["Research Nested Chat"]
        RM[Research Manager]
        subgraph RG["Research Group"]
            direction LR
            IAM_R[IAM Researcher]
            CW_R[CloudWatch Researcher]
            EC2_R[EC2 Researcher]
            EKS_R[EKS Researcher]
            VPC_R[VPC Researcher]
            Lambda_R[Lambda Researcher]
            ECS_R[ECS Researcher]
            S3_R[S3 Researcher]
            SNS_R[SNS Researcher]
            SQS_R[SQS Researcher]
            RDS_R[RDS Researcher]
            EC_R[ElastiCache Researcher]
            Aurora_R[Aurora Researcher]
        end
    end

    subgraph Solution["Solution Nested Chat"]
        SM[Solution Manager]
        subgraph SG["Specialist Group"]
            direction LR
            IAM_S[IAM Specialist]
            CW_S[CloudWatch Specialist]
            EC2_S[EC2 Specialist]
            EKS_S[EKS Specialist]
            VPC_S[VPC Specialist]
            Lambda_S[Lambda Specialist]
            ECS_S[ECS Specialist]
            S3_S[S3 Specialist]
            SNS_S[SNS Specialist]
            SQS_S[SQS Specialist]
            RDS_S[RDS Specialist]
            EC_S[ElastiCache Specialist]
            Aurora_S[Aurora Specialist]
        end
    end

    subgraph Expert["Expert Review Layer"]
        HE[Human Expert]
    end

    %% Connections
    U <--> UP
    UP <--> RC
    UP <--> SC
    UP <--> SV
    
    RC <--> RM
    SC <--> SM
    
    RM --- RG
    SM --- SG
    
    RC <--> HE
    SC <--> HE

    %% Styling
    classDef user fill:#f9f,stroke:#333,stroke-width:2px
    classDef coordinator fill:#bbf,stroke:#333,stroke-width:2px
    classDef manager fill:#ddf,stroke:#333,stroke-width:2px
    classDef agent fill:#dfd,stroke:#333,stroke-width:2px
    classDef expert fill:#fdd,stroke:#333,stroke-width:2px
    
    class U,UP user
    class RC,SC,SV coordinator
    class RM,SM manager
    class IAM_R,CW_R,EC2_R,EKS_R,VPC_R,Lambda_R,ECS_R,S3_R,SNS_R,SQS_R,RDS_R,EC_R,Aurora_R,IAM_S,CW_S,EC2_S,EKS_S,VPC_S,Lambda_S,ECS_S,S3_S,SNS_S,SQS_S,RDS_S,EC_S,Aurora_S agent
    class HE expert
```

## Prerequisites

- Python 3.8+
- OpenAI API key
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd aws-support-system
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # Unix/macOS
# or
.venv\Scripts\activate  # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure your OpenAI API key in `config.py`

## Usage

1. Start the system:

```bash
python main.py
```

2. Input Controls:

- `Enter` - Add new line
- `Ctrl+D` - Submit input
- `Ctrl+Q` - Quit application

3. Interaction Flow:
   - Enter your AWS-related question
   - Respond to clarifying questions
   - Review proposed solutions
   - Provide expert validation when requested

## Features in Detail

### 1. Multi-Agent Collaboration

- Nested chat architecture
- Specialized agent roles
- Dynamic conversation routing
- Expert validation workflow

### 2. Rich User Interface

- Multi-line input support
- Syntax highlighting
- Color-coded messages
- Clear formatting

### 3. Structured Solutions

- Step-by-step implementation guides
- Complete AWS CLI commands
- Infrastructure as Code examples
- Best practices and validations

### 4. Expert Review System

```
EXPERT REVIEW:
1. Technical Assessment
2. Security Review
3. Scalability & Reliability
4. Cost Considerations
5. Recommendations
```

### 5. Response Formats

```
CLARIFICATION NEEDED:
1. Specific questions
2. Reason for information

PROPOSED SOLUTION:
1. Overview
2. Implementation Steps
3. Validation
4. Monitoring
```

## Example Queries

- "How do I set up EKS node groups with monitoring?"
- "What's the best VPC design for a multi-tier application?"
- "How to implement cross-account IAM roles?"
- "Setting up CloudWatch dashboards for EKS clusters"

## Development

### Adding New Specialists

1. Create new specialist class in `specialists/`
2. Inherit from `BaseSpecialist`
3. Implement `create_specialist()` method
4. Add to `__init__.py` and `main.py`

### Customizing Prompts

- Modify `utils/input_handler.py` for input handling
- Update `chat_manager.py` for message formatting
- Adjust `config.py` for system-wide settings

## Architecture Details

### 1. Conversation Management

- Two-level chat structure
- Primary: User ↔ Coordinator
- Secondary: Coordinator ↔ Specialists + Expert

### 2. Message Flow

```
User Query → Coordinator → Specialist Group
                       ↓
User ← Coordinator ← Solution/Questions
```

### 3. Validation Flow

```
Solution → Human Expert → Validation
                      ↓
        Implementation/Revision
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
